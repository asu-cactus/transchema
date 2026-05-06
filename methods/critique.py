import time
import os
import pandas as pd
import numpy as np
import re
import traceback
import tiktoken
from pathlib import Path
from typing import Optional, Union
from hints.hint_v3 import get_column_equivalence
from hints.hints_static import get_hints_section, CRITIQUE_HINT_IDS
from auto_suggest_llm_util import (
    get_source,
    get_target_samples,
    get_filtered_functional_dependency,
)
from eval_score.score import relative_csv_score
from util.utils import execute_python, get_test_info
from llm.llm_models import TokenUsageTracker, LLMClient
from validation.hard_match import compare_lists_matching, compare_tables_matching, is_column_numerical
from validation.soft_match import compare_lists_matching_soft
from log_util.log_util import create_logger

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
from rag_pipeline.rag_layer import RAGDB, FeatureRAGDB, milvus_results_to_json
from rag_pipeline.feature_extractor import (
    compute_from_data,
    load_norm_stats,
    load_source_target_from_folder,
    parse_operation_history_for_query,
    zscore_normalize,
)


def resolve_rag_examples_base(
    rag_examples_base: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Resolve the path to the rag-examples-w-pipeline directory.

    This function provides a smart fallback to find the rag-examples-w-pipeline
    directory in common locations. Users can override by providing their own path
    or by setting the RAG_EXAMPLES_BASE environment variable.

    Args:
        rag_examples_base: Optional path to rag-examples-w-pipeline directory.
            If None, uses smart fallback (or RAG_EXAMPLES_BASE env var if set).
            Can be a string or Path object.

    Returns:
        Path object pointing to the rag-examples-w-pipeline directory.

    Raises:
        ValueError: If a provided path does not exist.
        FileNotFoundError: If no path could be resolved via fallback.

    Examples:
        >>> # Use default smart fallback (transchema/ or workspace root)
        >>> base = resolve_rag_examples_base()

        >>> # Override with custom path
        >>> base = resolve_rag_examples_base("/path/to/rag-examples-w-pipeline")
        >>> base = resolve_rag_examples_base(Path("/path/to/rag-examples-w-pipeline"))

        >>> # Or set environment variable: export RAG_EXAMPLES_BASE=/path/to/rag-examples-w-pipeline
    """
    # 1. Explicit parameter (highest priority)
    if rag_examples_base is not None:
        base_path = Path(rag_examples_base)
        if not base_path.exists():
            raise ValueError(
                f"Provided rag_examples_base path does not exist: {rag_examples_base}. "
                "Please ensure the directory exists or use None for automatic detection."
            )
        return base_path

    # 2. Environment variable
    env_path = os.environ.get("RAG_EXAMPLES_BASE")
    if env_path:
        base_path = Path(env_path)
        if base_path.exists():
            return base_path
        # If env is set but path invalid, warn but continue to fallback
        import warnings

        warnings.warn(
            f"RAG_EXAMPLES_BASE is set but path does not exist: {env_path}. "
            "Using automatic fallback.",
            UserWarning,
            stacklevel=2,
        )

    # 3. Smart fallback: transchema/ first, then workspace root
    transchema_dir = (
        Path(__file__).resolve().parent.parent
    )  # transchema/methods -> transchema
    workspace_root = transchema_dir.parent  # transchema -> workspace root

    base_path = transchema_dir / "examples_length_5_new"
    if base_path.exists():
        return base_path
    base_path = workspace_root / "examples_length_5_new"
    if base_path.exists():
        return base_path

    raise FileNotFoundError(
        "Could not find examples_length_5_new directory. "
        f"Tried: {transchema_dir / 'examples_length_5_new'}, "
        f"{workspace_root / 'examples_length_5_new'}. "
        "Provide the path via rag_examples_base parameter or RAG_EXAMPLES_BASE environment variable."
    )


def critique(
    args,
    length,
    id_,
    log_dir_,
    flags,
    is_def,
    operation_history,
    rag_examples_base: Optional[Union[str, Path]] = None,
    past_context_str: str = "",
    judge_reason: str = "",
):
    """
    Run critique on a data-pipeline transformation using RAG few-shot examples.

    When few_shot is enabled, retrieves similar documents from RAG, resolves their
    case IDs, and for each case loads the pipeline (operator_pipeline.txt) and
    Python code (python_recovered.py) from the rag-examples-w-pipeline directory,
    then injects them into the prompt as few-shot examples.

    Args:
        args: Configuration object (model, rag_db_uri, rag_topk, etc.).
        length: Length parameter (e.g., 4).
        id_: Target ID parameter (e.g., 32).
        log_dir_: Log directory path.
        flags: Tuple (fd_flag, metadata_flag, anon_flag, few_shot_flag).
        is_def: 1 for DEF_CRITIQUE, 0 for NEW_CRITIQUE.
        operation_history: History of operations for the current case.
        rag_examples_base: Optional path to rag-examples-w-pipeline directory.
            If None, uses resolve_rag_examples_base() (env RAG_EXAMPLES_BASE or
            automatic fallback). Can be str or Path. Use this to integrate
            with your own layout.

    Returns:
        Tuple (is_correct, cost, time_elapsed, score).

    Examples:
        >>> # Default (automatic path resolution)
        >>> result = critique(args, 4, 32, log_dir, flags, 0, history)

        >>> # Custom path for integration
        >>> result = critique(args, 4, 32, log_dir, flags, 0, history,
        ...                   rag_examples_base="/path/to/rag-examples-w-pipeline")
    """
    validate_fn = compare_tables_matching if getattr(args, "validation", "hard_match") == "autopipeline" else compare_lists_matching
    prompt_file = f"prompts/{args.critique_type}_critique.txt"

    with open(prompt_file, mode="r") as f:
        query = f.read()

    if args.static_hints:
        query = query.replace("$STATIC_HINTS$", get_hints_section(CRITIQUE_HINT_IDS, fmt="numbered"))
    else:
        query = query.replace("$STATIC_HINTS$", "")

    if past_context_str:
        query = query.replace("$PAST_ITERATION_CONTEXT$", past_context_str)
    else:
        query = query.replace("$PAST_ITERATION_CONTEXT$", "")

    if judge_reason:
        judge_reason_block = (
            f"Automated Judge Assessment:\n"
            f"The automated judge determined this output is INCORRECT.\n"
            f"Judge reasoning: \"{judge_reason}\""
        )
        query = query.replace("$JUDGE_REASON$", judge_reason_block)
    else:
        query = query.replace("$JUDGE_REASON$", "")

    log_dir = log_dir_

    # Benchmark selector: github | monteprep
    benchmark = getattr(args, "benchmark", "github")
    main_folder = "autopipeline-benchmarks/monteprep-pipelines" if benchmark == "monteprep" else "autopipeline-benchmarks/github-pipelines"
    path_to_files = f"{main_folder}/length{length}_{id_}/"
    # Counting files starting with 'test' in this subfolder
    file_count = sum(
        1
        for file in os.listdir(path_to_files)
        if file.startswith("test") and os.path.isfile(os.path.join(path_to_files, file))
    )

    ##print(file_count)
    if benchmark == "monteprep":
        json_file_path = "data/chatgpt_monteprep_ms.json" if file_count > 1 else "data/chatgpt_monteprep_ss.json"
    else:
        json_file_path = "data/chatgpt_github_ms.json" if file_count > 1 else "data/chatgpt_github_ss.json"

    len_id = length
    target_id = id_
    max_target_id = id_
    # anon_flag = flags[2]
    # fd = flags[0]
    # metadata_flag = flags[1]
    # few_shot_flag = flags[3]

    fd, metadata_flag, anon_flag, few_shot_flag = flags

    len_idx_target_idx = str(len_id) + "_" + str(target_id)

    token_tracker = TokenUsageTracker()

    start_time = time.time()

    if is_def == 1:
        type_ = "DEF_CRITIQUE"
    else:
        type_ = "NEW_CRITIQUE"

    logger = create_logger(type_, log_dir, len_id, target_id, max_target_id)

    if judge_reason:
        logger.info(f"JUDGE_CALL: judge={getattr(args, 'judge', 'unknown')} verdict=INCORRECT reason={judge_reason!r}")
    elif getattr(args, "judge", "gt") != "gt":
        logger.info(f"JUDGE_CALL: judge={args.judge} verdict=INCORRECT reason=(none)")

    llm_client = LLMClient(model=args.model, tracker=token_tracker, logger=logger)

    rag_db = None
    feature_rag_db = None
    feature_norm_stats = None
    if args.few_shot:
        if getattr(args, "rag_retrieval_strategy", "text") == "feature":
            feature_rag_db = FeatureRAGDB(
                uri=args.rag_db_uri,
                collection=getattr(
                    args, "rag_feature_collection", "plan_docs_features"
                ),
            )
            feature_norm_stats = load_norm_stats(
                getattr(args, "feature_norm_stats_path", None)
            )
        else:
            rag_db = RAGDB(
                uri=args.rag_db_uri,
                model_id=args.rag_embedding_model,
                collection=args.rag_db_collection,
                max_len=args.rag_embedding_dim,
            )

    # get schema
    (
        target_data_name,
        target_data_schema,
        target_data_schema_with_types,
        target_samples,
        file_count,
        source_data_name_list,
        source_data_schema_list,
        source_samples_list,
    ) = get_test_info(json_file_path, len_idx_target_idx, main_folder, anon_flag)

    # get model encoding
    if args.model == "gpt-4.1-mini":
        # According to https://github.com/openai/tiktoken/issues/395
        encoding = tiktoken.get_encoding("o200k_base")
    elif args.model == "o4-mini" or args.model == "o3":
        encoding = tiktoken.get_encoding("cl100k_base")
    else:
        encoding = tiktoken.encoding_for_model(args.model)

    num_tokens = args.token_limit

    num_target_samples = args.target_length

    num_source_samples = args.source_length

    # get target examples
    target_samples = get_target_samples(
        main_folder,
        len_idx_target_idx,
        0,
        False,
        num_target_samples,
        num_tokens,
        len(encoding.encode(query)),
        encoding,
    )
    if target_data_schema_with_types:
        query = query.replace("$SCHEMA$", target_data_schema_with_types)
    else:
        query = query.replace("$SCHEMA$", target_data_schema)
    query = query.replace("$EXAMPLES$", target_samples)

    # get source examples
    source_information = get_source(
        file_count,
        source_data_name_list,
        source_data_schema_list,
        main_folder,
        len_idx_target_idx,
        num_source_samples,
        num_tokens,
        encoding,
    )

    query = query.replace("$SRC_INFO$", source_information)

    ground_truth_location = (
        "{main_folder}/length{len_idx_target_idx}/target.csv".format(
            main_folder=main_folder, len_idx_target_idx=len_idx_target_idx
        )
    )
    try:
        df_ground_truth = pd.read_csv(ground_truth_location, low_memory=False)
        df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)
        query = query.replace("$NUM_TUPLES$", str(len(df_ground_truth)))
        if args.critique_type == "history":
            query = replace_history_info(query, operation_history)
            result_path = get_result_path(args, main_folder, len_idx_target_idx)
            query = replace_result_info(query, num_target_samples, result_path)
            try:
                df_generated = pd.read_csv(result_path, low_memory=False)
                # Load source CSVs for dtype context
                source_dfs = []
                for src_name in source_data_name_list:
                    try:
                        src_path = f"{main_folder}/length{len_idx_target_idx}/{src_name}"
                        source_dfs.append(pd.read_csv(src_path, index_col=0, low_memory=False))
                    except Exception:
                        pass
                dist_section = build_column_distribution_section(df_ground_truth, df_generated, source_dfs=source_dfs)
                query = query.replace("$COLUMN_DISTRIBUTIONS$", dist_section)
            except Exception:
                query = query.replace("$COLUMN_DISTRIBUTIONS$", "")
        else:
            query = query.replace("$COLUMN_DISTRIBUTIONS$", "")
    except Exception as e:
        query = query.replace("$NUM_TUPLES$", "Last python script failed to produce any output.")
        query = query.replace("$COLUMN_DISTRIBUTIONS$", "")

    if fd == 1:
        df_ground_truth_fd = df_ground_truth.sample(
            n=min(1000, df_ground_truth.shape[0]), replace=False
        )
        df_ground_truth_fd = df_ground_truth_fd.iloc[:, :15]
        key, fd__ = get_filtered_functional_dependency(df_ground_truth_fd)
        # fd_hints = get_fd_hints(key,fd__)
        fd_hints = "Keys : " + str(key) + "\n"
        fd_hints += "Functional Dependencies : " + str(fd__)
        query = query.replace("$FD_HINT$", fd_hints)
    else:
        query = query.replace("$FD_HINT$", "")

    if metadata_flag == 1:
        query = query.replace(
            "$METADATA$",
            "If the target data schema does not make sense, please suggest new column names that better represent the semantics of the columns.",
        )

    if few_shot_flag == 1:
        # Resolve rag-examples base path early (needed for feature strategy to load docs from disk)
        rag_examples_base_path = resolve_rag_examples_base(rag_examples_base)
        # try:
        #    logger.info(f"Using rag-examples-w-pipeline at: {rag_examples_base_path}")
        # except Exception:
        #    pass

        output_fields = args.rag_output_fields.split(",")
        if "case_id" not in output_fields:
            output_fields.append("case_id")

        if feature_rag_db is not None:
            # Feature-based retrieval: compute 23-dim from current task, search feature collection
            task_folder = Path(main_folder) / f"length{len_idx_target_idx}"
            pipeline_list = parse_operation_history_for_query(operation_history)
            try:
                logger.info(
                    "RAG_FEATURE_PIPELINE_AT_QUERY: operation_history=%s parsed_pipeline_list=%s",
                    operation_history,
                    pipeline_list,
                )
            except Exception:
                pass
            try:
                source_dfs, target_df = load_source_target_from_folder(task_folder)
                query_vector = compute_from_data(
                    source_dfs, target_df, pipeline_operator_list=pipeline_list or None
                )
            except Exception as e:
                try:
                    logger.warning(f"Feature extraction failed, using zero vector: {e}")
                except Exception:
                    pass
                query_vector = [0.0] * 23
            if feature_norm_stats is not None:
                query_vector = zscore_normalize(query_vector, feature_norm_stats)
            try:
                logger.info(f"RAG_FEATURE_QUERY_VECTOR (z-score normalized): {query_vector}")
            except Exception:
                pass
            rag_results = feature_rag_db.search(
                [query_vector],
                top_k=args.rag_topk,
                output_fields=["id", "case_id"],
                exclude_case_id=len_idx_target_idx,
            )
            rag_json_results = milvus_results_to_json(
                results=rag_results,
                output_fields=["id", "case_id"],
            )
            rag_json_results = [
                d for d in rag_json_results if d.get("case_id") != len_idx_target_idx
            ]
            seen_case_ids = set()
            deduped = []
            for d in rag_json_results:
                cid = d.get("case_id")
                if cid is None:
                    deduped.append(d)
                elif cid not in seen_case_ids:
                    seen_case_ids.add(cid)
                    deduped.append(d)
            rag_json_results = deduped[: args.rag_topk]
            # Load doc text from disk (feature collection does not store doc)
            for d in rag_json_results:
                cid = d.get("case_id")
                doc_text = ""
                if cid:
                    doc_path = (
                        rag_examples_base_path / f"Length{cid}" / f"Length{cid}.txt"
                    )
                    if doc_path.exists():
                        try:
                            doc_text = doc_path.read_text(
                                encoding="utf-8", errors="ignore"
                            ).strip()
                        except Exception:
                            pass
                d["doc"] = doc_text
        else:
            # Text-based retrieval (existing flow)
            aux_query = query if isinstance(query, list) else [query]
            rag_results = rag_db.search(
                aux_query,
                top_k=args.rag_topk,
                batch_size=args.rag_embedding_batch_size,
                output_fields=output_fields,
                exclude_case_id=len_idx_target_idx,
            )
            rag_json_results = milvus_results_to_json(
                results=rag_results,
                output_fields=output_fields,
            )
            rag_json_results = [
                d for d in rag_json_results if d.get("case_id") != len_idx_target_idx
            ]
            seen_case_ids = set()
            deduped = []
            for d in rag_json_results:
                cid = d.get("case_id")
                if cid is None:
                    deduped.append(d)
                elif cid not in seen_case_ids:
                    seen_case_ids.add(cid)
                    deduped.append(d)
            rag_json_results = deduped[: args.rag_topk]

        # Log retrieved documents explicitly (so we can audit retrieval without digging into the prompt).
        try:
            strategy = getattr(args, "rag_retrieval_strategy", "text")
            coll = (
                args.rag_db_collection
                if strategy == "text"
                else getattr(args, "rag_feature_collection", "plan_docs_features")
            )
            logger.info(
                f"RAG_RETRIEVAL: strategy={strategy} uri={args.rag_db_uri} collection={coll} top_k={args.rag_topk}"
            )
        except Exception:
            pass
        for idx, document in enumerate(rag_json_results):
            try:
                doc_id = document.get("id")
                distance = document.get("distance", document.get("score"))
                doc_text = document.get("doc", "")
                case_id = document.get("case_id", "N/A")
                preview = doc_text[:800].replace("\n", "\\n")
                logger.info(
                    f"RAG_HIT_{idx}: id={doc_id} case_id={case_id} distance={distance} preview={preview}"
                )
            except Exception:
                # Don't let logging failures break critique.
                pass

        few_shot_blocks = []
        for idx, document in enumerate(rag_json_results):
            case_id = document.get("case_id")
            doc_text = document.get("doc", "")

            # If case_id is not available, fallback to document text only
            if not case_id:
                few_shot_blocks.append(f"Few-shot Example {idx + 1}:\n{doc_text}")
                continue

            # Build folder path: case_id "4_24" → "Length4_24"
            folder_name = f"Length{case_id}"  # e.g., "Length4_24"
            case_folder = rag_examples_base_path / folder_name

            # Read pipeline and Python code files
            pipeline_content = ""
            python_code = ""

            pipeline_path = case_folder / "operator_pipeline.txt"
            python_path = case_folder / "python_recovered_successful.py"

            try:
                if pipeline_path.exists():
                    pipeline_content = pipeline_path.read_text(
                        encoding="utf-8", errors="ignore"
                    ).strip()
                else:
                    logger.warning(
                        f"Pipeline file not found for case {case_id}: {pipeline_path}"
                    )
            except Exception as e:
                logger.warning(f"Could not read pipeline for case {case_id}: {e}")

            try:
                if python_path.exists():
                    python_code = python_path.read_text(
                        encoding="utf-8", errors="ignore"
                    ).strip()
                else:
                    logger.warning(
                        f"Python code file not found for case {case_id}: {python_path}"
                    )
            except Exception as e:
                logger.warning(f"Could not read Python code for case {case_id}: {e}")

            # Build formatted block for this example
            block_parts = [f"Few-shot Example {idx + 1}:", doc_text]

            if pipeline_content:
                block_parts.append(f"\nPipeline for this few-shot example:")
                block_parts.append(pipeline_content)

            if python_code:
                block_parts.append(f"\nPython code for this few-shot example:")
                block_parts.append("```python")
                block_parts.append(python_code)
                block_parts.append("```")

            few_shot_blocks.append("\n".join(block_parts))

        # Join all blocks
        few_shot_prompt = "\n\n".join(few_shot_blocks)
        few_shot_prompt = "Here are some few shot examples:\n\n" + few_shot_prompt

        query = query.replace("$FEW_SHOT_EXAMPLES$", few_shot_prompt)

    res = llm_client.gpt(query)

    logger.info(query)
    logger.info(res[0])
    cost = token_tracker.cost_summary()
    logger.info(cost)

    try:
        with open(
            main_folder + "/length" + len_idx_target_idx + "/python_recovered.py",
            mode="r",
        ) as f:
            python_code = f.read()
    except Exception as e:
        python_code = ""
    target_location_critique = (
        main_folder
        + "/length"
        + len_idx_target_idx
        + "/target_multisource_critique_"
        + args.critique_type
        + ".csv"
    )
    query_generator = """Based on the LLM response, can you refine the python code."""
    if args.static_hints:
        query_generator += "\n\n" + get_hints_section(CRITIQUE_HINT_IDS, fmt="numbered") + "\n"
    query_generator += """
    Note : - Make sure to write the final output of the python code to {target_location_critique}
    - Make sure to write the python code in-between "```Python" and "```"
    - Please keep the final output columns the same as it was in the python script given. [Strictly do not add prefix or suffix to the column names]
    - You just need to apply the fix according to the criticizer response.
    - Do not use assignment operation for any column.
    Python Code : ```Python 
    {python_code}
    ```

    Code fixing suggestions : ```
    {res}
    ```
    """.format(
        python_code=python_code,
        target_location_critique=target_location_critique,
        res=res,
    )

    res_gen = llm_client.gpt(query_generator)

    pattern = re.compile(r"```Python(.*?)```", re.DOTALL | re.IGNORECASE)
    match = pattern.search(res_gen[0])
    script = match.group(1).strip()

    if script:
        with open(
            f"{main_folder}/length{length}_{id_}/python_recovered.py",
            "w",
        ) as file:
            file.write(script)

    logger.info(query_generator)
    logger.info(res_gen[0])
    logger.info(token_tracker.cost_summary())
    cost = token_tracker.cost_summary()
    end_time = time.time()
    time_elapsed = end_time - start_time
    print(script)
    response = execute_python(script)
    print(response)
    # sys.exit()
    logger.info(response)

    df_critique = None
    fd_f1_val = 0.0
    col_ratio_val = 0.0
    debug_dict_val = {}

    try:
        df_critique = pd.read_csv(target_location_critique, low_memory=False)
        (
            case_accuracy,
            is_correct,
            similarity_scores,
            shared_columns,
        ) = validate_fn(df_critique, df_ground_truth)
        if (
            is_correct == False
            and len(shared_columns) > 0
            and len(df_ground_truth) == len(df_critique)
        ):
            print(
                "TRY IGNORING COLUMN HEADERS AND SORTING COLUMNS FOR BETTER COMPARISON:"
            )
            sorted_df_critique = df_critique.sort_values(by=shared_columns)
            sorted_df_ground_truth = df_ground_truth.sort_values(by=shared_columns)
            new_header_critique = []
            for col in sorted_df_critique.columns:
                if "float" in str(sorted_df_critique[col].dtype):
                    print("is float")
                    first_three_values = sorted_df_critique[col].head(3).astype(int)
                else:
                    print("is not float")
                    first_three_values = sorted_df_critique[col].head(3)
                concatenated_header = (
                    str(first_three_values.iloc[0])
                    + "-"
                    + str(first_three_values.iloc[1])
                    + "-"
                    + str(first_three_values.iloc[2])
                )
                new_header_critique.append(concatenated_header)
            sorted_df_critique.columns = new_header_critique
            new_header_ground_truth = []
            for col in sorted_df_ground_truth.columns:
                if "float" in str(sorted_df_ground_truth[col].dtype):
                    print("is float")
                    first_three_values = sorted_df_ground_truth[col].head(3).astype(int)
                else:
                    print("is not float")
                    first_three_values = sorted_df_ground_truth[col].head(3)
                concatenated_header = (
                    str(first_three_values.iloc[0])
                    + "-"
                    + str(first_three_values.iloc[1])
                    + "-"
                    + str(first_three_values.iloc[2])
                )
                new_header_ground_truth.append(concatenated_header)
            sorted_df_ground_truth.columns = new_header_ground_truth
            print("OUR RESPONSE:")
            print(sorted_df_critique)
            print("GROUND TRUTH:")
            print(sorted_df_ground_truth)
            (
                case_accuracy,
                is_correct,
                similarity_scores,
                shared_columns,
            ) = validate_fn(sorted_df_critique, sorted_df_ground_truth)
            _, col_ratio_val, _, fd_f1_val, score, debug_dict_val = relative_csv_score(sorted_df_critique, sorted_df_ground_truth)
        else:
            _, col_ratio_val, _, fd_f1_val, score, debug_dict_val = relative_csv_score(df_critique, df_ground_truth)
        logger.info(is_correct)

    except Exception as e:
        is_correct = False
        score = 0
        print("".join(traceback.format_exc()))

    crit_info = (
        is_correct,
        cost.get("total_cost", 0.0),
        time_elapsed,
        score,
    )
    return crit_info, (df_critique, fd_f1_val, col_ratio_val, score, debug_dict_val)


def replace_history_info(query, operation_history):
    return query.replace("$OPERATIONS$", operation_history)


def build_column_distribution_section(
    df_gt: pd.DataFrame,
    df_gen: pd.DataFrame,
    source_dfs: list = None,
) -> str:
    """
    Per-column distribution comparison between the ground-truth and generated tables.
    Numeric columns: min, max, mean with range/mean ratio warnings.
    Categorical columns: unique count and top values.
    Also reports source column dtypes when source_dfs is provided.
    Also reports missing/extra columns.
    """
    lines = ["Column-Level Distribution Comparison (Target vs Generated):"]

    # Show source table schemas upfront so the LLM knows the original dtypes
    # (target columns are often renamed/aggregated from source columns)
    if source_dfs:
        lines.append("\n  Source Table Column Schemas:")
        for src_idx, src_df in enumerate(source_dfs):
            col_dtypes = ", ".join(f"{c}({src_df[c].dtype})" for c in src_df.columns)
            lines.append(f"    src_{src_idx}: {col_dtypes}")

    # Build a flat lookup: col_name_lower -> list of (source_file_idx, dtype)
    # Used for exact-name matches (non-renamed columns)
    source_dtype_map: dict = {}
    if source_dfs:
        for src_idx, src_df in enumerate(source_dfs):
            for col in src_df.columns:
                key = col.lower()
                if key not in source_dtype_map:
                    source_dtype_map[key] = []
                source_dtype_map[key].append((src_idx, str(src_df[col].dtype)))

    gt_cols_lower  = {c.lower(): c for c in df_gt.columns}
    gen_cols_lower = {c.lower(): c for c in df_gen.columns}
    shared = sorted(set(gt_cols_lower) & set(gen_cols_lower))

    for col_lower in shared:
        gt_col  = gt_cols_lower[col_lower]
        gen_col = gen_cols_lower[col_lower]
        gt_series  = df_gt[gt_col].dropna()
        gen_series = df_gen[gen_col].dropna()

        gt_dtype  = str(df_gt[gt_col].dtype)
        gen_dtype = str(df_gen[gen_col].dtype)

        # Build dtype summary line
        if gt_dtype != gen_dtype:
            dtype_note = f" [dtype mismatch: target={gt_dtype}, generated={gen_dtype}]"
        else:
            dtype_note = f" [dtype: {gt_dtype}]"

        # Append source dtype info if available
        src_entries = source_dtype_map.get(col_lower)
        if src_entries:
            src_dtype_str = ", ".join(f"src_{i}={dt}" for i, dt in src_entries)
            dtype_note += f" [source: {src_dtype_str}]"

        lines.append(f"\n  Column '{gt_col}'{dtype_note}:")

        try:
            gt_vals  = gt_series.astype(float).values
            gen_vals = gen_series.astype(float).values
            gt_min,  gt_max,  gt_mean  = float(gt_vals.min()),  float(gt_vals.max()),  float(gt_vals.mean())
            gen_min, gen_max, gen_mean = float(gen_vals.min()), float(gen_vals.max()), float(gen_vals.mean())

            lines.append(f"    Target   : min={gt_min:.4g},  max={gt_max:.4g},  mean={gt_mean:.4g}")
            lines.append(f"    Generated: min={gen_min:.4g}, max={gen_max:.4g}, mean={gen_mean:.4g}")

            # gt_range  = gt_max  - gt_min
            # gen_range = gen_max - gen_min
            # if gt_range > 1e-6:
            #     ratio = gen_range / gt_range
            #     if ratio > 5:
            #         lines.append(
            #             f"    WARNING: generated range is {ratio:.1f}x larger than target — "
            #             "likely SUM used instead of AVG or COUNT."
            #         )
            #     elif ratio < 0.2:
            #         lines.append(
            #             f"    WARNING: generated range is {ratio:.2f}x of target — "
            #             "possible over-aggregation or wrong GROUP BY."
            #         )

            # if abs(gt_mean) > 1e-6:
            #     mean_ratio = gen_mean / gt_mean
            #     if mean_ratio > 5:
            #         lines.append(
            #             f"    WARNING: generated mean is {mean_ratio:.1f}x larger than target — "
            #             "consider AVG instead of SUM."
            #         )
            #     elif mean_ratio < 0.2:
            #         lines.append(
            #             f"    WARNING: generated mean is {mean_ratio:.2f}x of target — "
            #             "values may be under-aggregated."
            #         )

        except (ValueError, TypeError):
            gt_nunique  = int(gt_series.nunique())
            gen_nunique = int(gen_series.nunique())
            gt_top  = gt_series.value_counts().head(5).index.tolist()
            gen_top = gen_series.value_counts().head(5).index.tolist()
            lines.append(f"    Target   : {gt_nunique} unique values, top: {gt_top}")
            lines.append(f"    Generated: {gen_nunique} unique values, top: {gen_top}")
            # if gt_nunique != gen_nunique:
            #     lines.append(
            #         f"    WARNING: unique value counts differ ({gt_nunique} vs {gen_nunique}) — "
            #         "check string normalization or grouping."
            #     )

    missing = sorted(set(df_gt.columns) - set(df_gen.columns))
    extra   = sorted(set(df_gen.columns) - set(df_gt.columns))
    if missing:
        lines.append(f"\n  Columns in target but MISSING in generated: {missing}")
    if extra:
        lines.append(f"  Columns in generated but NOT in target: {extra}")

    return "\n".join(lines)


def get_result_path(args, main_folder, len_idx_target_idx):

    if args.intermediate_materialization:
        result_path = f"{main_folder}/intermediate_space/length{len_idx_target_idx}/"
        # Find the highest-numbered intermediate_step{n}.csv in the folder
        max_step = 0
        for f in os.listdir(result_path):
            if f.startswith("intermediate_step") and f.endswith(".csv"):
                try:
                    step = int(f[len("intermediate_step"):-len(".csv")])
                    max_step = max(max_step, step)
                except ValueError:
                    pass
        result_path += f"intermediate_step{max_step}.csv"
    elif getattr(args, "single_step_cot", False):
        result_path = f"{main_folder}/length{len_idx_target_idx}/target_multisource_cot.csv"
    else:
        result_path = f"{main_folder}/length{len_idx_target_idx}/target_multisource.csv"

    return result_path


def replace_result_info(query, num_result_samples, result_path):
    # Read result file as a DataFrame and get column names to replace $RES_SCHEMA$ in the query;
    # Get first batch of rows as examples to replace $RES_EXAMPLES$ in the query
    df_result = pd.read_csv(result_path, low_memory=False)
    res_schema = ", ".join(df_result.columns)
    res_examples = df_result.head(num_result_samples).to_string(index=False)
    query = query.replace("$RES_SCHEMA_NOT_AVAILABLE$", res_schema)
    query = query.replace("$NUM_RES_TUPLES_NOT_AVAILABLE$", str(len(df_result)))
    query = query.replace("$RES_EXAMPLES_NOT_AVAILABLE$", res_examples)
    return query
