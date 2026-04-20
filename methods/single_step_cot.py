import time
from llm.llm_models import TokenUsageTracker, LLMClient
from validation.hard_match import compare_lists_matching, compare_tables_matching
from util.utils import get_test_info
from test_scope import get_test_cases_ids
from methods.multi_step import Config, get_python_response

from log_util.log_util import create_logger
from eval_score.score import relative_csv_score
import pandas as pd
import os
import traceback


def single_step_cot(args, length, id_, log_dir_, experiment_name, i_, past_context_str=""):
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
    # Counting files starting with 'test' in this subfolder
    file_count = sum(
        1
        for _, _, files in os.walk(path_to_files)
        for file in files
        if file.startswith("test")
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
        ) = get_test_info(json_file_path, len_idx_target_idx, main_folder, anon_flag)
        # added anon_flag to get_test_info() call

        llm_client = LLMClient(model=model, tracker=token_tracker, logger=logger)

        
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
                    _, col_ratio_val, _, fd_f1_val, score, debug_dict_val = relative_csv_score(df_our_response, df_ground_truth)
                except Exception as e:
                    print("".join(traceback.format_exc()))
            except Exception as e:
                print("".join(traceback.format_exc()))
                case_accuracy = 0
                is_correct = False
                score = 0

    end_time = time.time()

    # Only try to write the file if script was actually generated
    if script:
        with open(
            f"{main_folder}/length{length}_{id_}/python_recovered.py",
            "w",
        ) as file:
            file.write(script)
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
