# cot.py
import time
import os
import re
import traceback
from pathlib import Path

import pandas as pd

from llm.llm_models import TokenUsageTracker, LLMClient
from validation.hard_match import compare_lists_matching
from validation.soft_match import compare_lists_matching_soft
from util.utils import get_test_info, execute_python
from test_scope import get_test_cases_ids
from auto_suggest_llm_util import (
    calculate_score,
    get_prompt,
    query_gpt,
)
from log_util.log_util import create_logger


def _extract_script_from_response(resp_text: str) -> str:
    """
    Robustly extract a Python code block from an LLM response.
    (Case-insensitive; falls back to any fenced block.)
    """
    pattern = re.compile(r"```Python(.*?)```", re.DOTALL | re.IGNORECASE)
    match = pattern.search(resp_text or "")
    if not match:
        pattern_generic = re.compile(r"```(python)?(.*?)```", re.DOTALL | re.IGNORECASE)
        match = pattern_generic.search(resp_text or "")
        if match:
            body = (
                match.group(2)
                if match.lastindex and match.lastindex >= 2
                else match.group(1)
            )
            return (body or "").strip()
        return ""
    return match.group(1).strip()


def _try_hard_match_with_fallback(
    df_our_response: pd.DataFrame, df_ground_truth: pd.DataFrame
):
    """
    Apply the comparison flow used in multistep.py:
      1) Hard match
      2) If fail & same length & have shared columns -> sort on first shared col,
         synthesize headers from first 3 values, re-compare.
    Returns: (case_accuracy, is_correct, similarity_scores)
    """
    case_accuracy, is_correct, similarity_scores, shared_columns = (
        compare_lists_matching(df_our_response, df_ground_truth)
    )

    if (
        (not is_correct)
        and len(shared_columns) > 0
        and len(df_our_response) == len(df_ground_truth)
    ):
        print("TRY IGNORING COLUMN HEADERS AND SORTING COLUMNS FOR BETTER COMPARISON:")
        key_col = shared_columns[0]

        sorted_df_our = df_our_response.sort_values(by=key_col)
        sorted_df_gt = df_ground_truth.sort_values(by=key_col)

        new_header_our = []
        for col in sorted_df_our.columns:
            first_three = sorted_df_our[col].head(3).astype(str)
            new_header_our.append("-".join(first_three))
        sorted_df_our.columns = new_header_our

        new_header_gt = []
        for col in sorted_df_gt.columns:
            first_three = sorted_df_gt[col].head(3).astype(str)
            new_header_gt.append("-".join(first_three))
        sorted_df_gt.columns = new_header_gt

        print("OUR RESPONSE:")
        print(sorted_df_our)
        print("GROUND TRUTH:")
        print(sorted_df_gt)

        case_accuracy, is_correct, similarity_scores, _ = compare_lists_matching(
            sorted_df_our, sorted_df_gt
        )

    return case_accuracy, is_correct, similarity_scores


def cot(args, length, id_, log_dir_, experiment_name, i_):
    """
    CoT (single-prompt) version mirroring multistep.py’s I/O.
    Args are the same as multistep.multi_step(...).
    Returns:
        (is_correct, total_cost, time_elapsed, score, op_hist_)
    """
    # Initialize common variables (aligned with multistep.py)
    case_path = f"{length}_{id_}"
    is_correct = False
    score = 0
    cost_summary = []
    start_time = time.time()
    token_tracker = TokenUsageTracker()
    script = ""
    op_hist_ = ""

    # Pull parameters from args
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

    # Paths & bookkeeping
    path_to_files = f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/"
    file_count = sum(
        1
        for _, _, files in os.walk(path_to_files)
        for file in files
        if file.startswith("test")
    )

    json_file_path = (
        "data/chatgpt_github_ms.json"
        if file_count > 1
        else "data/chatgpt_github_ss.json"
    )
    log_dir = log_dir_
    main_folder = "autopipeline-benchmarks/github-pipelines"

    allowed_operation_list = [
        "JOIN",
        "UNION",
        "GROUP_BY/AGGREGATE",
        "PIVOT",
        "UNPIVOT",
        "NO_MORE_OPERATION",
    ]

    task_list = get_test_cases_ids(
        json_file_path, len_id, max_len_id, target_id, max_target_id
    )

    logger = create_logger("COT", log_dir, len_id, target_id, max_target_id)

    q_count = {"total": 0, "in_task": 0}

    # Process each task (same loop structure as multistep.py)
    for task in task_list:
        q_count["in_task"] = 0
        logger.info("Started Experiment for : " + str(task))

        cost_summary = []
        token_tracker = TokenUsageTracker()
        cost_summary.append(token_tracker.cost_summary())

        len_idx_target_idx = task[6:]

        # New get_test_info signature (with types)
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

        llm_client = LLMClient(model=model, tracker=token_tracker, logger=logger)

        # One-shot CoT prompt that both DECIDES and PRODUCES the script
        # (You should define this 'cot_script' branch inside get_prompt)
        target_file_location = (
            "{main_folder}/length{len_idx_target_idx}/target_multisource.csv".format(
                main_folder=main_folder, len_idx_target_idx=len_idx_target_idx
            )
        )
        ground_truth_location = (
            "{main_folder}/length{len_idx_target_idx}/target.csv".format(
                main_folder=main_folder, len_idx_target_idx=len_idx_target_idx
            )
        )

        script_cnt = 0
        error_str = ""
        response = ""
        while script_cnt < 5:
            prompt = get_prompt(
                prompt_type="cot_script",  # single-prompt decision + code generation
                max_tokens=token_limit,
                model=model,
                allowed_operation_list=allowed_operation_list,
                operation_history=[],  # no iterative history in CoT mode
                target_data_name=target_data_name,
                target_data_schema=target_data_schema,
                target_data_schema_with_types=target_data_schema_with_types,
                target_samples=target_samples,
                file_count=file_count,
                source_data_name_list=source_data_name_list,
                source_data_schema_list=source_data_schema_list,
                directory=main_folder,
                len_idx_target_idx=len_idx_target_idx,
                target_perc=target_per,
                is_perc=is_perc,
                target_length=target_length,
                source_length=source_length,
                join_flag=join_flag,
                aggregate_flag=aggregate_flag,
                join_hints_truncate=join_hints_truncate,
                aggregate_hints_truncate=aggregate_hints_truncate,
                hint_source=hint_source,
                few_shot=few_shot,
                save_path=target_file_location,  # align with multistep python_script
                error_string=error_str,
            )

            if prompt[0] == "-1":
                logger.info("Token Limit Exceeded")
                break

            res = query_gpt(
                llm_client,
                model,
                prompt,
                q_count,
                logger,
                cost_summary,
                token_tracker,
                type="CoT Decide + Script",
            )

            try:
                script = _extract_script_from_response(res[0])
                response = execute_python(script)
                error_str = error_str + response + "\n"
                if response == "Success":
                    break
            except Exception:
                print("".join(traceback.format_exc()))
                error_str = error_str + "No valid response from LLM.\n"
                response = ""
            script_cnt += 1

        if response == "Success":

            print(script)
            print(response)
            # archive script (same as multistep.py)
            # archive_dir = f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/script_archive"
            # if not os.path.exists(archive_dir):
            #     os.makedirs(archive_dir)
            # with open(f"{archive_dir}/{experiment_name}_{i_}.py", "w") as f:
            #     f.write(script)

            try:
                df_our_response = pd.read_csv(target_file_location, low_memory=False)
                df_ground_truth = pd.read_csv(ground_truth_location, low_memory=False)

                # Drop first column (index-like) as in multistep.py
                df_ground_truth.drop(
                    columns=df_ground_truth.columns[0], axis=1, inplace=True
                )

                try:
                    (
                        case_accuracy,
                        is_correct,
                        similarity_scores,
                        shared_columns,
                    ) = compare_lists_matching(df_our_response, df_ground_truth)
                    """
                        print(
                            case_accuracy, is_correct, similarity_scores, shared_columns
                        )
                        """
                    if (
                        is_correct == False
                        and len(shared_columns) > 0
                        and len(df_our_response) == len(df_ground_truth)
                    ):
                        print(
                            "TRY IGNORING COLUMN HEADERS AND SORTING COLUMNS FOR BETTER COMPARISON:"
                        )
                        sorted_df_our_response = df_our_response.sort_values(
                            by=shared_columns[0]
                        )
                        sorted_df_ground_truth = df_ground_truth.sort_values(
                            by=shared_columns[0]
                        )
                        new_header_our_response = []
                        for col in sorted_df_our_response.columns:
                            first_three_values = (
                                sorted_df_our_response[col].head(3).astype(str)
                            )
                            concatenated_header = "-".join(first_three_values)
                            new_header_our_response.append(concatenated_header)
                        sorted_df_our_response.columns = new_header_our_response
                        new_header_ground_truth = []
                        for col in sorted_df_ground_truth.columns:
                            first_three_values = (
                                sorted_df_ground_truth[col].head(3).astype(str)
                            )
                            concatenated_header = "-".join(first_three_values)
                            new_header_ground_truth.append(concatenated_header)
                        sorted_df_ground_truth.columns = new_header_ground_truth
                        print("OUR RESPONSE:")
                        print(sorted_df_our_response)
                        print("GROUND TRUTH:")
                        print(sorted_df_ground_truth)
                        (
                            case_accuracy,
                            is_correct,
                            similarity_scores,
                            shared_columns,
                        ) = compare_lists_matching(
                            sorted_df_our_response, sorted_df_ground_truth
                        )
                    else:
                        score = calculate_score(df_ground_truth, df_our_response)
                except Exception as e:
                    print("".join(traceback.format_exc()))
                    is_correct = False
            except Exception as e:
                print("".join(traceback.format_exc()))
                case_accuracy = 0
                is_correct = False
                score = 0
        op_hist_ = str("")
    end_time = time.time()

    # Save last recovered script (same as multistep.py)
    if script:
        with open(
            f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/python_recovered.py",
            "w",
        ) as f:
            f.write(script)

    # Compose return like multistep.ms_info
    cost_data = token_tracker.cost_summary()
    total_cost = cost_data.get("total_cost", 0.0)
    time_elapsed = end_time - start_time
    ms_info = (
        is_correct,
        total_cost,
        time_elapsed,
        score,
        op_hist_,
    )
    print(f"ms_info: {ms_info}")
    logger.info("Total Queries Made : {q}".format(q=q_count["total"]))
    return ms_info
