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
import argparse
import pdb
import os

from test_scope import get_test_cases_ids
from llm.llm_models import TokenUsageTracker, LLMClient
from util.utils import (
    get_test_info,
    execute_python,
)

from validation.hard_match import compare_lists_matching
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

import parameters as p

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
        shutil.copy(file, source_space_path)
    return source_space_dir


def get_operation(res):
    last_line = res.split("\n")[-1]
    match = re.search(r"\$(.*?)\$", last_line)
    if match:
        operation = match.group(1)
    else:
        raise Exception(f"Operation not found in the response. Response:\n{res}")
    assert (
        operation in allowed_operation_list
    ), f"Operation not in allowed list: {repr(operation)}"
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
        pdb.set_trace()
    assert (
        operation in allowed_operation_list
    ), f"Operation not in allowed list: {operation}"
    return operation, configuration


def get_operator(llm_client, operation_history, nth_intermediate_step, p, config):

    if p.use_old_prompt:
        # Overwrite nth_intermediate_step=0 to use the old prompt, i.e., no intermediate materialization
        nth_intermediate_step = 0

    prompt = get_prompt(
        prompt_type="get_next_operator",
        max_tokens=p.token_limit,
        model=p.model,
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_name=config["target_data_name"],
        target_data_schema=config["target_data_schema"],
        target_samples=config["target_samples"],
        file_count=config["file_count"],
        source_data_name_list=config["source_data_name_list"],
        source_data_schema_list=config["source_data_schema_list"],
        directory=config["source_space_dir"],
        len_idx_target_idx=config["len_idx_target_idx"],
        target_perc=p.target_per,
        is_perc=p.is_perc,
        target_length=p.target_length,
        source_length=p.source_length,
        fd_flag=p.fd_flag,
        hint_source=p.hint_source,
        nth_intermediate_step=nth_intermediate_step,
        combine_ask_and_configure=p.combine_ask_and_configure,
        no_thinking=p.no_thinking,
    )

    res = query_gpt(
        llm_client,
        p.model,
        prompt,
        config["q_count"],
        config["logger"],
        config["cost_summary"],
        config["token_tracker"],
        type="Ask For Operator",
    )[0]

    if p.use_old_prompt or not  p.combine_ask_and_configure:
        operation = get_operation(res)
        assert operation in allowed_operation_list
        return operation, None
    else:
        try:
            operation, configuration = get_operation_and_configuration(res)
        except Exception as e:
            print(res)
            pdb.set_trace()

        if configuration.lower() == "none":
            configuration = None
        return operation, configuration


def configure_operator(llm_client, operation, operation_history, nth_intermediate_step, config):
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

        prompt = get_prompt(
            prompt_type=prompt_type_mapping[operation],
            max_tokens=p.token_limit,
            model=p.model,
            allowed_operation_list=allowed_operation_list,
            operation_history=operation_history,
            target_data_name=config["target_data_name"],
            target_data_schema=config["target_data_schema"],
            target_samples=config["target_samples"],
            file_count=config["file_count"],
            source_data_name_list=config["source_data_name_list"],
            source_data_schema_list=config["source_data_schema_list"],
            directory=config["source_space_dir"],
            len_idx_target_idx=config["len_idx_target_idx"],
            target_perc=p.target_per,
            is_perc=p.is_perc,
            target_length=p.target_length,
            join_flag=p.join_flag,
            join_hints_truncate=p.join_hints_truncate,
            fd_flag=p.fd_flag,
            hint_source=p.hint_source,
            nth_intermediate_step=nth_intermediate_step,
        )

        res = query_gpt(
            config["llm_client"],
            p.model,
            prompt,
            config["q_count"],
            config["logger"],
            config["cost_summary"],
            config["token_tracker"],
            type=query_gpt_type_mappping[operation],
        )
    else:
        return

    if operation == "JOIN":
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



def materialize_chatgpt(llm_client, operation_history, save_path, nth_intermediate_step, config):
    n_trails = 5
    error_str = ""

    for script_cnt in range(n_trails):
        prompt = get_prompt(
            prompt_type="python_script",
            max_tokens=p.token_limit,
            model=p.model,
            allowed_operation_list=allowed_operation_list,
            operation_history=operation_history,
            target_data_name=config["target_data_name"],
            target_data_schema=config["target_data_schema"],
            target_samples=config["target_samples"],
            file_count=config["file_count"],
            source_data_name_list=config["source_data_name_list"],
            source_data_schema_list=config["source_data_schema_list"],
            directory=config["source_space_dir"],
            len_idx_target_idx=config["len_idx_target_idx"],
            target_perc=p.target_per,
            is_perc=p.is_perc,
            target_length=p.target_length,
            error_string=error_str,
            fd_flag=p.fd_flag,
            hint_source=p.hint_source,
            save_path=save_path,
            nth_intermediate_step=nth_intermediate_step,
        )

        res = query_gpt(
            config["llm_client"],
            p.model,
            prompt,
            config["q_count"],
            config["logger"],
            config["cost_summary"],
            config["token_tracker"],
            type="Get Python Script",
        )[0]

        script = res.split("```Python")[1].split("```")[0].strip()

        response = execute_python(script)
        print(f"Python execution: {response}")
        config["logger"].info(f"Python execution: {response}")
        error_str += response + "\n"

        if response == "Success":
            return

    raise Exception(f"Exceed {n_trails} trails, Materialization Failed")



def get_task(logger,json_file_path, len_id, max_len_id, target_id, max_target_id):
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
    df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)
    hard_avg_similarity, is_correct, similarity_scores, validation_error = (
        compare_lists_matching(df_our_response, df_ground_truth)
    )
    log_str = f"Hard comparison, {config["task"]=}, {hard_avg_similarity=},  {is_correct=}, {similarity_scores=}"
    print(log_str)
    logger.info(log_str)
    # logger.info(validation_error)
    soft_avg_similarity, is_correct, similarity_scores = compare_lists_matching_soft(
        df_our_response, df_ground_truth
    )
    log_str = f"Soft comparison, {config["task"]=}, {soft_avg_similarity=},  {is_correct=}, {similarity_scores=}"
    print(log_str)
    logger.info(log_str)

    return (
        is_correct,
        hard_avg_similarity,
        soft_avg_similarity,
    )


#################################################################################################################################

def intermediate_materialization(length, id_, log_dir_, experiment_name,i_):
    len_id = length
    max_len_id = length
    target_id = id_
    max_target_id = id_
    use_old_prompt = p.use_old_prompt
    log_dir = log_dir_

    main_folder = "autopipeline-benchmarks/github-pipelines"

    path_to_files = f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/"
    # Counting files starting with 'test' in this subfolder
    file_count = sum(
        1
        for _, _, files in os.walk(path_to_files)
        for file in files
        if file.startswith("test")
    )
    
    #print(file_count)

    if file_count > 1:
        json_file_path = "data/chatgpt_github_ms.json"
    else:            
        json_file_path = "data/chatgpt_github_ss.json"

    source_space_dir = create_source_space(main_folder, len_id, target_id)

    # logging
    logger = create_logger("materialization", log_dir, len_id, target_id, max_target_id)
    task = get_task(logger,json_file_path, len_id, max_len_id, target_id, max_target_id)

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

    llm_client = LLMClient(model=p.model, tracker=token_tracker, logger=logger)

    # configure all the remaining parameters used by later functions
    config = {}
    config["q_count"] = q_count
    config["cost_summary"] = cost_summary
    config["token_tracker"] = token_tracker
    config["logger"] = logger
    config["llm_client"] = llm_client
    config["source_space_dir"] = source_space_dir
    config["len_idx_target_idx"] = len_idx_target_idx
    config["target_data_name"] = target_data_name
    config["target_data_schema"] = target_data_schema
    config["target_samples"] = target_samples
    config["file_count"] = file_count
    config["source_data_name_list"] = source_data_name_list
    config["source_data_schema_list"] = source_data_schema_list
    config["source_samples_list"] = source_samples_list
    config["main_folder"] = main_folder

    # materialization_criteria = MaterializationCriteria()

    max_operations = 5
    for nth_intermediate_step in range(1, max_operations + 1):

        # Get the operation
        operation, configuration = get_operator(
            llm_client, operation_history, nth_intermediate_step,  p, config
        )

        if operation == "NO_MORE_OPERATION":
            print("No More Operation")
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
                config
            )
        print(operation_history)

        # Materialize the operation
        intermediate_filename = f"intermediate_step{nth_intermediate_step}"
        save_path = (
            f"{source_space_dir}/length{len_idx_target_idx}/{intermediate_filename}.csv"
        )
        materialize_chatgpt(
            llm_client,
            operation_history,
            save_path,
            nth_intermediate_step,
            config
        )
        if not use_old_prompt:
            source_data_name_list.append(intermediate_filename)

        is_correct, _, _ = verify_result(
            save_path,
            f"{main_folder}/length{len_idx_target_idx}/target.csv",
        )
        if is_correct:
            print("Successful transformation")
            break

    if nth_intermediate_step > 1:
        # Do the final verification
        _, hard_avg_similarity, soft_avg_similarity = verify_result(
            save_path,
            f"{main_folder}/length{len_idx_target_idx}/target.csv",
        )
        # Append hard_avg_similarity and soft_avg_similarity to a csv file "results/materialization.csv"
        result_dir = Path("results")
        result_dir.mkdir(exist_ok=True, parents=True)
        if  p.use_old_prompt:
            file_name = "old_prompt.csv"
        elif  p.combine_ask_and_configure:
            # With "combine ask for and configure", thinking is enable.
            file_name = "combine_ask_and_configure.csv"
        elif  p.no_thinking:
            # With no thinking, "Ask for operation" and "Configure operation" are seperated
            file_name = "no_thinking.csv"
        else:
            # Default setting is not combining ask for and configure, and thinking is enable.
            file_name = "default.csv"

        result_file = result_dir / file_name
        if not result_file.exists():
            with open(result_file, "w") as f:
                f.write("task,hard_avg_similarity,soft_avg_similarity\n")
        with open(result_file, "a") as f:
            f.write(f"{task},{hard_avg_similarity},{soft_avg_similarity}\n")
