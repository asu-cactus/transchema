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

from test_scope import get_test_cases_ids
from llm.llm_models import TokenUsageTracker, LLMClient
from util.utils import (
    get_test_info,
    execute_python,
    compare_lists_matching,
    compare_lists_matching_soft,
)

# import auto_suggest_llm_prompts as prt
from auto_suggest_llm_util import (
    create_logger,
    get_columns,
    query_gpt,
    get_columns_join,
    get_prompt,
)

import pandas as pd

# decided through parameters

target_per = 25
is_perc = False
hint_source = "v3"


# 2
# target_length = int(max(3,10*0.9695545786258186))
# source_length = int(max(3,10*0.09828012752411708))

# 3
target_length = int(max(3, 10 * 0.31342417815924284))
source_length = int(max(3, 10 * 0.9682615757193975))

join_flag = 0
aggregate_flag = 0
fd_flag = 1
token_limit = 120000
model = "gpt-4.1-mini"  # "gpt-4-turbo" # "gpt-3.5-turbo-16k" # "gpt-4-1-mini"


# 2
# join_hints_truncate = [0.9006759015810097,0.11102115895485554,0.5241539295936876,0.021526354616419163,0.9722678489028443,0.5997167278729312]
# aggregate_hints_truncate = [0.9006759015810097,0.5797659415180153,0.46440152668695256,0.8109176073751933]

# 3
# join_hints = [dvr, js, jc, vro, leftness, sortedness]
# aggregate_hints = [dvr_ub,dvr_lb, leftness_ub,leftness_lb, emptiness_ub,emptiness_lb, peak_frequency_ub, peak_frequency_lb,value_range_ub, value_range_lb]
join_hints_truncate = [
    0.027387593197926163,
    0.8763891522960383,
    0.6923226156693141,
    0.8946066635038473,
    0.14038693859523377,
    0.8007445686755367,
]
aggregate_hints_truncate = [0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1]


json_file_path = "data/chatgpt_github_ms.json"
log_dir = "logs-materialization-v1-text-fd"
main_folder = "autopipeline-benchmarks/github-pipelines"
source_space_name = "source_space"

allowed_operation_list = [
    "JOIN",
    "UNION",
    "GROUP_BY/AGGREGATE",
    "PIVOT",
    "UNPIVOT",
    "NO_MORE_OPERATION",
]

q_count = {"total": 0, "in_task": 0}


def parse_args():
    parser = argparse.ArgumentParser(description="Intermediate Materialization")
    parser.add_argument(
        "--len_id", type=int, default=2, help="Length ID for the test case"
    )
    parser.add_argument(
        "--target_id", type=int, default=2, help="Target ID for the test case"
    )
    parser.add_argument(
        "--use_old_prompt", action="store_true", help="Use new prompt or not"
    )
    parser.add_argument(
        "--combine_ask_and_configure",
        action="store_true",
        help="Combine ask for and configure an operations.",
    )
    parser.add_argument(
        "--no_thinking", action="store_true", help="Disable thinking process"
    )
    args = parser.parse_args()
    return args


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


def get_operator(llm_client, operation_history, nth_intermediate_step, args):

    if args.use_old_prompt:
        # Overwrite nth_intermediate_step=0 to use the old prompt, i.e., no intermediate materialization
        nth_intermediate_step = 0

    prompt = get_prompt(
        prompt_type="get_next_operator",
        max_tokens=token_limit,
        model=model,
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_name=target_data_name,
        target_data_schema=target_data_schema,
        target_samples=target_samples,
        file_count=file_count,
        source_data_name_list=source_data_name_list,
        source_data_schema_list=source_data_schema_list,
        directory=source_space_dir,
        len_idx_target_idx=len_idx_target_idx,
        target_perc=target_per,
        is_perc=is_perc,
        target_length=target_length,
        source_length=source_length,
        fd_flag=fd_flag,
        hint_source=hint_source,
        nth_intermediate_step=nth_intermediate_step,
        combine_ask_and_configure=args.combine_ask_and_configure,
        no_thinking=args.no_thinking,
    )

    res = query_gpt(
        llm_client,
        model,
        prompt,
        q_count,
        logger,
        cost_summary,
        token_tracker,
        type="Ask For Operator",
    )[0]

    if args.use_old_prompt or not args.combine_ask_and_configure:
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


def configure_operator(llm_client, operation, operation_history, nth_intermediate_step):

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
            max_tokens=token_limit,
            model=model,
            allowed_operation_list=allowed_operation_list,
            operation_history=operation_history,
            target_data_name=target_data_name,
            target_data_schema=target_data_schema,
            target_samples=target_samples,
            file_count=file_count,
            source_data_name_list=source_data_name_list,
            source_data_schema_list=source_data_schema_list,
            directory=source_space_dir,
            len_idx_target_idx=len_idx_target_idx,
            target_perc=target_per,
            is_perc=is_perc,
            target_length=target_length,
            join_flag=join_flag,
            join_hints_truncate=join_hints_truncate,
            fd_flag=fd_flag,
            hint_source=hint_source,
            nth_intermediate_step=nth_intermediate_step,
        )

        res = query_gpt(
            llm_client,
            model,
            prompt,
            q_count,
            logger,
            cost_summary,
            token_tracker,
            type=query_gpt_type_mappping[operation],
        )
    else:
        pass

    if operation == "JOIN":
        joined_columns = get_columns_join(res[0])
        # history_elements.append(joined_columns)
        operation_history.append(f"{operation} : {joined_columns}")

    elif operation == "GROUP_BY/AGGREGATE":
        # add it to the history
        group_by_column = re.sub(r"```json\n|\n|```", "", res[0])
        # history_elements.append(res)
        operation_history.append(group_by_column)
        # operation_history.append(operation + ' : [ group_by : {group_by_column[0]}, aggregate : {group_by_column[1]}, aggregation_function : {group_by_column[2]} ]'.format(group_by_column = group_by_column))

    elif operation == "UNION":
        tables_ = get_columns(res[0])
        # history_elements.append(tables_)
        operation_history.append(operation + " : " + str(tables_))
    else:
        operation_history.append(operation)


def materialize_chatgpt(
    llm_client, operation_history, save_path, nth_intermediate_step
):
    n_trails = 5
    error_str = ""
    for script_cnt in range(n_trails):
        prompt = get_prompt(
            prompt_type="python_script",
            max_tokens=token_limit,
            model=model,
            allowed_operation_list=allowed_operation_list,
            operation_history=operation_history,
            target_data_name=target_data_name,
            target_data_schema=target_data_schema,
            target_samples=target_samples,
            file_count=file_count,
            source_data_name_list=source_data_name_list,
            source_data_schema_list=source_data_schema_list,
            directory=source_space_dir,
            len_idx_target_idx=len_idx_target_idx,
            target_perc=target_per,
            is_perc=is_perc,
            target_length=target_length,
            error_string=error_str,
            fd_flag=fd_flag,
            hint_source=hint_source,
            save_path=save_path,
            nth_intermediate_step=nth_intermediate_step,
        )

        res = query_gpt(
            llm_client,
            model,
            prompt,
            q_count,
            logger,
            cost_summary,
            token_tracker,
            type="Get Python Script",
        )[0]

        script = res.split("```Python")[1].split("```")[0].strip()

        response = execute_python(script)
        print(f"Python execution: {response}")
        logger.info(f"Python execution: {response}")
        error_str = error_str + response + "\n"
        # print(error_str)
        if response == "Success":
            return
    raise Exception(f"Exceed {n_trails} trails, Materialization Failed")


def get_task(logger):
    task_list = get_test_cases_ids(
        json_file_path, len_id, max_len_id, target_id, max_target_id
    )
    task = task_list[0]

    logger.info("Started Experiment for : " + str(task))
    return task


def verify_result(target_file_location, ground_truth_location):

    df_our_response = pd.read_csv(target_file_location, low_memory=False)
    df_ground_truth = pd.read_csv(ground_truth_location, low_memory=False)
    df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)
    hard_avg_similarity, is_correct, similarity_scores, validation_error = (
        compare_lists_matching(df_our_response, df_ground_truth)
    )
    log_str = f"Hard comparison, {task=}, {hard_avg_similarity=},  {is_correct=}, {similarity_scores=}"
    print(log_str)
    logger.info(log_str)
    # logger.info(validation_error)
    soft_avg_similarity, is_correct, similarity_scores = compare_lists_matching_soft(
        df_our_response, df_ground_truth
    )
    log_str = f"Soft comparison, {task=}, {soft_avg_similarity=},  {is_correct=}, {similarity_scores=}"
    print(log_str)
    logger.info(log_str)

    return (
        is_correct,
        hard_avg_similarity,
        soft_avg_similarity,
    )


#################################################################################################################################

if __name__ == "__main__":
    args = parse_args()

    len_id = args.len_id
    max_len_id = len_id
    target_id = args.target_id
    max_target_id = target_id
    use_old_prompt = args.use_old_prompt

    source_space_dir = create_source_space(main_folder, len_id, target_id)
    logger = create_logger("materialization", log_dir, len_id, target_id, max_target_id)
    task = get_task(logger)

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

    llm_client = LLMClient(model=model, tracker=token_tracker, logger=logger)

    # materialization_criteria = MaterializationCriteria()

    max_operations = 5
    for nth_intermediate_step in range(1, max_operations + 1):

        # Get the operation
        operation, configuration = get_operator(
            llm_client, operation_history, nth_intermediate_step, args
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
        if args.use_old_prompt:
            file_name = "old_prompt.csv"
        elif args.combine_ask_and_configure:
            # With "combine ask for and configure", thinking is enable.
            file_name = "combine_ask_and_configure.csv"
        elif args.no_thinking:
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