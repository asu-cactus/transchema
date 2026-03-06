"""Intermediate Materialization Algorithm

while Stopping Criteria
    get operation and configure
    op_hist = op_hist + (op,conf)
    if materialization_criteria
        mat_table = materialize(source,op_hist)
        source_space = source_space - source_op_hist + mat_table
        op_hist = []

"""

import re
from pathlib import Path
import shutil
import pdb
import os
import time

from test_scope import get_test_cases_ids
from llm.llm_models import TokenUsageTracker, LLMClient
from util.utils import (
    get_test_info,
    execute_python,
)

from validation.hard_match import compare_lists_matching, compare_tables_matching
from validation.soft_match import compare_lists_matching_soft

# import auto_suggest_llm_prompts as prt
from auto_suggest_llm_util import (
    get_columns,
    query_gpt,
    get_columns_join,
    get_prompt,
)

from log_util.log_util import create_logger

import pandas as pd

# decided through parameters
source_space_name = "source_space"

allowed_operation_list = [
    "JOIN",
    "UNION",
    "GROUP_BY/AGGREGATE",
    "PIVOT",
    "UNPIVOT",
    "NO_MORE_OPERATION",
]


def create_source_space(main_folder, len_id, target_id):
    # create source space
    source_space_dir = f"{main_folder}/{source_space_name}"
    source_space_path = Path(f"{source_space_dir}/length{len_id}_{target_id}")
    source_space_path.mkdir(exist_ok=True, parents=True)

    source_dir = Path(f"{main_folder}/length{len_id}_{target_id}")
    # Find all files matching the pattern "test{integer}.csv" in the source directory
    for file in source_dir.glob("*"):
        if file.is_file():  # Skip directories
            shutil.copy(file, source_space_path)
    return source_space_dir


def get_operation(res):
    last_line = res.split("\n")[-1]
    match = re.search(r"\$(.*?)\$", last_line)
    if match:
        operation = match.group(1)
    else:
        raise Exception(f"Operation not found in the response. Response:\n{res}")
    # assert (
    #     operation in allowed_operation_list
    # ), f"Operation not in allowed list: {repr(operation)}"
    return operation


def get_operation_and_configuration(res):
    last_line = res.split("\n")[-1]
    match = re.search(
        r"Next operation after operation history is \$(.*)\$ and configuration is \$(.*)\$",
        last_line,
    )
    if match:
        operation = match.group(1)
        configuration = match.group(2)
    else:
        print(f"Last line:\n{last_line}")
        return None, "none"
    # assert (
    #   operation in allowed_operation_list
    # ), f"Operation not in allowed list: {operation}"
    return operation, configuration


def get_operator(llm_client, operation_history, nth_intermediate_step, args, config):

    # print("Get Operator-"+str(nth_intermediate_step))
    prompt = get_prompt(
        prompt_type="get_next_operator",
        max_tokens=args.token_limit,
        model=args.model,
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_name=config["target_data_name"],
        target_data_schema=config["target_data_schema_with_types"],
        target_samples=config["target_samples"],
        file_count=config["file_count"],
        source_data_name_list=config["source_data_name_list"],
        source_data_schema_list=config["source_data_schema_list"],
        directory=config["source_space_dir"],
        len_idx_target_idx=config["len_idx_target_idx"],
        target_perc=args.target_per,
        is_perc=args.is_perc,
        target_length=args.target_length,
        source_length=args.source_length,
        fd_flag=args.fd_flag,
        hint_source=args.hint_source,
        nth_intermediate_step=nth_intermediate_step,
        combine_ask_and_configure=args.combine_ask_and_configure,
        no_thinking=args.no_thinking,
    )

    # print("Prompt is" + prompt)

    operation = None
    max_tries = 5
    while operation is None and max_tries > 0:
        max_tries -= 1

        res = query_gpt(
            llm_client,
            args.model,
            prompt,
            config["q_count"],
            config["logger"],
            config["cost_summary"],
            config["token_tracker"],
            type="Ask For Operator",
        )[0]

        # print("Response is"+res)

        if not args.combine_ask_and_configure:
            operation = get_operation(res)
            print(operation)
            if operation in allowed_operation_list:
                return operation, None
            else:
                # print(operation)
                return operation, None
        else:
            operation, configuration = get_operation_and_configuration(res)
            if operation is None:
                continue

            if configuration.lower() == "none":
                configuration = None
            return operation, configuration

    if max_tries == 0:
        raise Exception(f"Failed to get operation after 5 tries. Last response:\n{res}")


def configure_operator(
    llm_client, operation, operation_history, nth_intermediate_step, args, config
):
    if operation in ["JOIN", "UNION", "GROUP_BY/AGGREGATE"]:
        prompt_type_mapping = {
            "JOIN": "join",
            "UNION": "union",
            "GROUP_BY/AGGREGATE": "group_by_aggregate",
        }
        query_gpt_type_mappping = {
            "JOIN": "Configure Join",
            "UNION": "Configure Union",
            "GROUP_BY/AGGREGATE": "Configure Group by/Aggergate",
        }
        print("To configure operator")
        prompt = get_prompt(
            prompt_type=prompt_type_mapping[operation],
            max_tokens=args.token_limit,
            model=args.model,
            allowed_operation_list=allowed_operation_list,
            operation_history=operation_history,
            target_data_name=config["target_data_name"],
            target_data_schema=config["target_data_schema_with_types"],
            target_samples=config["target_samples"],
            file_count=config["file_count"],
            source_data_name_list=config["source_data_name_list"],
            source_data_schema_list=config["source_data_schema_list"],
            directory=config["source_space_dir"],
            len_idx_target_idx=config["len_idx_target_idx"],
            target_perc=args.target_per,
            is_perc=args.is_perc,
            target_length=args.target_length,
            source_length=args.source_length,
            join_flag=args.join_flag,
            join_hints_truncate=args.join_hints_truncate,
            fd_flag=args.fd_flag,
            hint_source=args.hint_source,
            nth_intermediate_step=nth_intermediate_step,
        )

        print("To query GPT")

        res = query_gpt(
            config["llm_client"],
            args.model,
            prompt,
            config["q_count"],
            config["logger"],
            config["cost_summary"],
            config["token_tracker"],
            type=query_gpt_type_mappping[operation],
        )

        print(res)

    else:
        return

    if operation == "JOIN":
        print("get_columns_join")
        joined_columns = get_columns_join(res[0])
        operation_history.append(f"{operation} : {joined_columns}")
    elif operation == "GROUP_BY/AGGREGATE":
        group_by_column = re.sub(r"```json\n|\n|```", "", res[0])
        operation_history.append(group_by_column)
    elif operation == "UNION":
        tables_ = get_columns(res[0])
        operation_history.append(operation + " : " + str(tables_))
    else:
        operation_history.append(operation)


def materialize_chatgpt(
    operation_history, save_dir, nth_intermediate_step, args, config
):
    n_trails = 5
    error_str = ""

    for _ in range(n_trails):
        prompt = get_prompt(
            prompt_type="python_script",
            max_tokens=args.token_limit,
            model=args.model,
            allowed_operation_list=allowed_operation_list,
            operation_history=operation_history,
            target_data_name=config["target_data_name"],
            target_data_schema=config["target_data_schema_with_types"],
            target_samples=config["target_samples"],
            file_count=config["file_count"],
            source_data_name_list=config["source_data_name_list"],
            source_data_schema_list=config["source_data_schema_list"],
            directory=config["source_space_dir"],
            len_idx_target_idx=config["len_idx_target_idx"],
            target_perc=args.target_per,
            is_perc=args.is_perc,
            target_length=args.target_length,
            source_length=args.source_length,
            error_string=error_str,
            fd_flag=args.fd_flag,
            hint_source=args.hint_source,
            save_path=f"{save_dir}/intermediate_step{nth_intermediate_step}.csv",
            nth_intermediate_step=nth_intermediate_step,
        )

        res = query_gpt(
            config["llm_client"],
            args.model,
            prompt,
            config["q_count"],
            config["logger"],
            config["cost_summary"],
            config["token_tracker"],
            type="Get Python Script",
        )[0]

        # print(res)
        # res = res[0]
        # print("+++")
        # print(res)
        pattern = re.compile(r"```Python(.*?)```", re.DOTALL | re.IGNORECASE)
        match = pattern.search(res)
        script = match.group(1).strip()

        response = execute_python(script)
        print(f"Python execution: {response}")
        config["logger"].info(f"Python execution: {response}")
        error_str += response + "\n"

        if response == "Success":
            # Save the result to the python_recovered.py from where it will be picked up for critique
            save_path = f"{save_dir}/python_step{nth_intermediate_step}.py"
            with open(save_path, "w") as f:
                f.write(script)
            return save_path

    raise Exception(f"Exceed {n_trails} trails, Materialization Failed")


def get_task(logger, json_file_path, len_id, max_len_id, target_id, max_target_id):
    task_list = get_test_cases_ids(
        json_file_path, len_id, max_len_id, target_id, max_target_id
    )
    task = task_list[0]

    logger.info("Started Experiment for : " + str(task))
    return task


def verify_result(target_file_location, ground_truth_location, config):
    logger = config["logger"]
    df_our_response = pd.read_csv(target_file_location, low_memory=False)
    df_ground_truth = pd.read_csv(ground_truth_location, low_memory=False)
    # if (is_column_numerical(df_ground_truth.columns[0])):
    df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)
    try:
        (
            hard_avg_similarity,
            hard_is_correct,
            hard_similarity_scores,
            _,
        ) = config.get("validate_fn", compare_lists_matching)(df_our_response, df_ground_truth)

    except Exception as e:
        hard_avg_similarity = 0.0
        hard_is_correct = False
        hard_similarity_scores = []

        log_str = "Hard comparison failed, " + str(e)
        print(log_str)
        logger.info(log_str)

    log_str = f"Hard comparison, {config['task']=}, {hard_avg_similarity=},  {hard_is_correct=}, {hard_similarity_scores=}"
    print(log_str)
    logger.info(log_str)

    hard_match_result = {
        "avg_similarity": hard_avg_similarity,
        "is_correct": hard_is_correct,
        "similarity_scores": hard_similarity_scores,
    }
    return hard_match_result


#################################################################################################################################


def intermediate_materialization(args, length, id_, log_dir_, experiment_name, i_):
    start_time = time.time()
    len_id = length
    max_len_id = length
    target_id = id_
    max_target_id = id_
    log_dir = log_dir_

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

    # print(file_count)

    if benchmark == "monteprep":
        json_file_path = "data/chatgpt_monteprep_ms.json" if file_count > 1 else "data/chatgpt_monteprep_ss.json"
    else:
        json_file_path = "data/chatgpt_github_ms.json" if file_count > 1 else "data/chatgpt_github_ss.json"

    source_space_dir = create_source_space(main_folder, len_id, target_id)

    # logging
    logger = create_logger("materialization", log_dir, len_id, target_id, max_target_id)
    task = get_task(
        logger, json_file_path, len_id, max_len_id, target_id, max_target_id
    )

    q_count = {"total": 0, "in_task": 0}

    cost_summary = []
    operation_history = []

    token_tracker = TokenUsageTracker()
    cost_summary.append(token_tracker.cost_summary())
    # print(cost_summary)

    len_idx_target_idx = task.lstrip("Target")

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
    ) = get_test_info(
        json_file_path,
        len_idx_target_idx,
        main_folder,
        anon_flag=0,
    )

    llm_client = LLMClient(model=args.model, tracker=token_tracker, logger=logger)

    # configure all the remaining parameters used by later functions
    config = {}
    config["q_count"] = q_count
    config["cost_summary"] = cost_summary
    config["token_tracker"] = token_tracker
    config["logger"] = logger
    config["llm_client"] = llm_client
    config["validate_fn"] = compare_tables_matching if getattr(args, "validation", "hard_match") == "autopipeline" else compare_lists_matching
    config["source_space_dir"] = source_space_dir
    config["len_idx_target_idx"] = len_idx_target_idx
    config["target_data_name"] = target_data_name
    config["target_data_schema"] = target_data_schema
    if target_data_schema_with_types:
        config["target_data_schema_with_types"] = target_data_schema_with_types
    else:
        config["target_data_schema_with_types"] = target_data_schema
    config["target_samples"] = target_samples
    config["file_count"] = file_count
    config["source_data_name_list"] = source_data_name_list
    config["source_data_schema_list"] = source_data_schema_list
    config["source_samples_list"] = source_samples_list
    config["main_folder"] = main_folder
    config["source_space_dir"] = source_space_dir
    config["task"] = task

    # materialization_criteria = MaterializationCriteria()

    max_operations = 9
    for nth_intermediate_step in range(1, max_operations + 1):
        # print("**Step-" + str(nth_intermediate_step))
        try:
            # Get the operation
            operation, configuration = get_operator(
                llm_client, operation_history, nth_intermediate_step, args, config
            )

            # print("Next Operator:"+operation)

            if operation == "NO_MORE_OPERATION":
                # print("No More Operation")
                logger.info("No More Operation")
                break

            # Configure the operation
            if configuration is not None:
                operation_history.append(f"{operation} : {configuration}")
            else:
                configure_operator(
                    llm_client,
                    operation,
                    operation_history,
                    nth_intermediate_step,
                    args,
                    config,
                )
            print(operation_history)

            # Materialize the operation
            save_dir = f"{source_space_dir}/length{len_idx_target_idx}"
            intermediate_filename = f"intermediate_step{nth_intermediate_step}"
            save_path = f"{save_dir}/{intermediate_filename}.csv"

            materialize_chatgpt(
                operation_history, save_dir, nth_intermediate_step, args, config
            )
        except Exception as e:
            print(f"Materialization failed: {e}")
            logger.error(f"Materialization failed: {e}")
            # Use the last intermediate step if available
            if nth_intermediate_step == 1:
                save_path = f"{source_space_dir}/length{len_idx_target_idx}/test_0.csv"
            else:
                intermediate_filename = f"intermediate_step{nth_intermediate_step - 1}"
                save_path = f"{source_space_dir}/length{len_idx_target_idx}/{intermediate_filename}.csv"
            break

        source_data_name_list.append(intermediate_filename)

        hard_match_result = verify_result(
            save_path,
            f"{main_folder}/length{len_idx_target_idx}/target.csv",
            config,
        )
        if hard_match_result["is_correct"]:
            end_time = time.time()
            ms_info = (
                hard_match_result["is_correct"],
                token_tracker.cost_summary().get(
                    "total_cost", 0.0
                ),  # Use the extracted total_cost value
                end_time - start_time,
                0,
                str(operation_history),
            )
            print("Successful transformation")
            return ms_info

    # Do the final verification
    hard_match_result = verify_result(
        save_path, f"{main_folder}/length{len_idx_target_idx}/target.csv", config
    )

    end_time = time.time()
    time_elapsed = end_time - start_time
    cost_data = token_tracker.cost_summary()  # This returns a dictionary
    total_cost = cost_data.get("total_cost", 0.0)
    ms_info = (
        hard_match_result["is_correct"],
        total_cost,  # Use the extracted total_cost value
        time_elapsed,
        0,
        str(operation_history),
    )
    return ms_info
