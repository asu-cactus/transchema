import time
from llm.llm_models import TokenUsageTracker, LLMClient
from validation.hard_match import compare_lists_matching, compare_tables_matching
from util.utils import get_test_info, execute_python, make_test_validation_script
from test_scope import get_test_cases_ids
from methods.multi_step import Config, get_python_response

from log_util.log_util import create_logger
from eval_score_value_based import value_based_relative_csv_score_timed
from rag_pipeline.local_rag_db import build_upper_bound_db, get_rag_hints
import pandas as pd
import os
import traceback


def single_step_cot(args, length, id_, log_dir_, experiment_name, i_, past_context_str="", token_tracker=None, budget=None):
    # Initialize required variables
    case_path = f"{length}_{id_}"
    is_correct = False
    is_correct_ = False
    case_accuracy_ = 0
    score = 0
    case_accuracy = 0
    df_our_response = None
    fd_f1_val = 0.0
    col_ratio_val = 0.0
    debug_dict_val = {}
    validate_fn = compare_tables_matching if getattr(args, "validation", "hard_match") == "autopipeline" else compare_lists_matching
    cost_summary = []
    start_time = time.time()
    if token_tracker is None:
        token_tracker = TokenUsageTracker()
    script = ""
    op_hist_ = ""
    hint_source = args.hint_source
    len_id = length
    max_len_id = length
    target_id = id_
    max_target_id = id_
    target_per = args.target_per
    is_perc = args.is_perc
    anon_flag = args.anon_flag
    target_length = args.target_length
    source_length = args.source_length
    join_flag = args.join_flag
    aggregate_flag = args.aggregate_flag
    join_hints_truncate = args.join_hints_truncate
    aggregate_hints_truncate = args.aggregate_hints_truncate
    few_shot = args.few_shot

    fd_flag = args.fd_flag
    token_limit = args.token_limit
    model = args.model
    # Benchmark selector: github | monteprep
    benchmark = getattr(args, "benchmark", "github")
    main_folder = "autopipeline-benchmarks/monteprep-pipelines" if benchmark == "monteprep" else "autopipeline-benchmarks/github-pipelines"
    path_to_files = f"{main_folder}/length{length}_{id_}/"
    data_split = getattr(args, "data_split", "test")
    # Counting files starting with data_split prefix in this subfolder (root only, no subdirs)
    file_count = sum(
        1
        for file in os.listdir(path_to_files)
        if os.path.isfile(os.path.join(path_to_files, file))
        if file.startswith(data_split)
    )

    if benchmark == "monteprep":
        json_file_path = "data/chatgpt_monteprep_ms.json" if file_count > 1 else "data/chatgpt_monteprep_ss.json"
    else:
        json_file_path = "data/chatgpt_github_ms.json" if file_count > 1 else "data/chatgpt_github_ss.json"

    log_dir = log_dir_

    task_list = get_test_cases_ids(
        json_file_path, len_id, max_len_id, target_id, max_target_id
    )

    logger = create_logger("AUTOSUGGEST", log_dir, len_id, target_id, max_target_id)

    q_count = {"total": 0, "in_task": 0}

    # Create configuration for LLM calls
    directory = main_folder

    # language = 'sql' #or 'python'

    ################## Run for each task ##################

    # For single_step_cot called with specific length/id, construct the task name directly
    task_list = [f"Target{length}_{id_}"]

    for task in task_list:

        q_count["in_task"] = 0

        logger.info("Started Experiment for : " + str(task))

        cost_summary = []

        start_time = time.time()
        token_tracker = TokenUsageTracker()
        cost_summary.append(token_tracker.cost_summary())
        len_idx_target_idx = task[6:]

        # Get the information of the target and source data

        (
            target_data_name,
            target_data_schema,
            target_data_schema_with_types,
            target_samples,
            file_count,
            source_data_name_list,
            source_data_schema_list,
            source_samples_list,
        ) = get_test_info(json_file_path, len_idx_target_idx, main_folder, anon_flag, data_split=data_split)
        # added anon_flag and data_split to get_test_info() call

        llm_client = LLMClient(model=model, tracker=token_tracker, logger=logger, cost_budget=budget if budget is not None else 0.0)

        # Build local RAG DB and retrieve hints (upper_bound mode)
        rag_mode = getattr(args, "rag", "none")
        sscot_rag_hints = ""
        if rag_mode == "upper_bound":
            gt_csv = getattr(args, "gt_csv", "ground_truth_pipelines.csv")
            db_path = f"/tmp/rag_upper_bound_{length}_{id_}.db"
            try:
                build_upper_bound_db(
                    case_id=f"{length}_{id_}",
                    case_folder=os.path.join(main_folder, f"length{length}_{id_}"),
                    gt_csv_path=gt_csv,
                    db_path=db_path,
                )
                sscot_rag_hints = get_rag_hints(db_path, [])
                if sscot_rag_hints:
                    logger.info(f"[sscot RAG] hints retrieved for {length}_{id_}")
                else:
                    logger.info(f"[sscot RAG] no matching hints for {length}_{id_}")
            except Exception:
                logger.warning(f"[sscot RAG] failed to build/query RAG DB:\n{traceback.format_exc()}")

        config = Config(
            target_data_name=target_data_name,
            target_data_schema=target_data_schema,
            target_data_schema_with_types=target_data_schema_with_types,
            target_samples=target_samples,
            file_count=file_count,
            source_data_name_list=source_data_name_list,
            source_data_schema_list=source_data_schema_list,
            len_idx_target_idx=len_idx_target_idx,
            target_perc=target_per,
            is_perc=is_perc,
            target_length=target_length,
            source_length=source_length,
            fd_flag=fd_flag,
            hint_source=hint_source,
            llm_client=llm_client,
            q_count=q_count,
            logger=logger,
            cost_summary=cost_summary,
            token_tracker=token_tracker,
            model=model,
            token_limit=token_limit,
            directory=directory,
            static_hints=getattr(args, "static_hints", True),
            past_context=past_context_str,
            rag_hints=sscot_rag_hints,
            data_split=data_split,
        )


        ground_truth_location = f"{main_folder}/length{len_idx_target_idx}/target.csv"
        target_file_location = (
            f"{main_folder}/length{len_idx_target_idx}/target_multisource_cot.csv"
        )
        script, response, _ = get_python_response([], 0, target_file_location, config)

        if response == "Success":
            # save file here
            # file_name
            if not os.path.exists(f"{main_folder}/length{length}_{id_}/script_archive"):
                os.makedirs(f"{main_folder}/length{length}_{id_}/script_archive")
            with open(
                f"{main_folder}/length{length}_{id_}/script_archive/{experiment_name}_{i_}_cot.py",
                "w",
            ) as file:
                file.write(script)

            try:
                df_our_response = pd.read_csv(target_file_location, low_memory=False)
                df_ground_truth = pd.read_csv(ground_truth_location, low_memory=False)
                df_ground_truth.drop(
                    columns=df_ground_truth.columns[0], axis=1, inplace=True
                )
                try:
                    (
                        case_accuracy,
                        is_correct,
                        similarity_scores,
                        _,
                    ) = validate_fn(df_our_response, df_ground_truth)
                except Exception as e:
                    print("".join(traceback.format_exc()))
                    is_correct = False
                try:
                    _, col_ratio_val, _, fd_f1_val, score, debug_dict_val = value_based_relative_csv_score_timed(df_our_response, df_ground_truth)
                except Exception as e:
                    print("".join(traceback.format_exc()))
            except Exception as e:
                print("".join(traceback.format_exc()))
                case_accuracy = 0
                is_correct = False
                score = 0

    # Two-phase validation: score on training output, is_correct on test output
    if data_split == "training" and script:
        test_script = make_test_validation_script(script)
        test_output = f"{main_folder}/length{length}_{id_}/target_multisource_cot_test_val.csv"
        print("[two-phase sscot] executing test-data script for is_correct validation...")
        test_exec = execute_python(test_script)
        if test_exec == "Success" and os.path.exists(test_output):
            try:
                df_test = pd.read_csv(test_output, low_memory=False)
                df_gt_test = pd.read_csv(ground_truth_location, low_memory=False)
                df_gt_test.drop(columns=df_gt_test.columns[0], axis=1, inplace=True)
                _, test_is_correct, _, _ = validate_fn(df_test, df_gt_test)
                print(f"[two-phase sscot] is_correct: training={is_correct} → test={test_is_correct}")
                is_correct = test_is_correct
            except Exception:
                print(f"[two-phase sscot] test validation failed:\n{traceback.format_exc()}")
        else:
            print(f"[two-phase sscot] test exec={test_exec}, output_exists={os.path.exists(test_output)}")

    end_time = time.time()

    # Only try to write the file if script was actually generated
    if script:
        recovered_path = f"{main_folder}/length{length}_{id_}/python_recovered.py"
        with open(recovered_path, "w") as file:
            file.write(script)
        print(f"[single_step_cot] python_recovered.py written: {recovered_path}")
    cost_data = token_tracker.cost_summary()  # This returns a dictionary
    total_cost = cost_data.get("total_cost", 0.0)  # Safely get total_cost with default
    time_elapsed = end_time - start_time
    ms_info = (
        is_correct,
        total_cost,  # Use the extracted total_cost value
        time_elapsed,
        score,
        op_hist_,
    )
    print(f"ms_info: {ms_info}")
    logger.info("Total Queries Made : {q}".format(q=q_count["total"]))

    return ms_info, (df_our_response, fd_f1_val, col_ratio_val, score, debug_dict_val)
