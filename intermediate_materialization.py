# intermediate Materialization Algorithm

# while Stopping Criteria
#     get operation and configure
#     op_hist = op_hist + (op,conf)
#     if materialization_criteria
#         mat_table = materialize(source,op_hist)
#         source_space = source_space - source_op_hist + mat_table
#         op_hist = []


from test_scope import get_test_cases_ids
from llm.llm_models import TokenUsageTracker, LLMClient
from util.utils import (
    get_test_info,
    execute_python,
    compare_lists_matching,
    compare_lists_matching_soft,
)
import parameters as p
import pdb

# import auto_suggest_llm_prompts as prt
from auto_suggest_llm_util import (
    create_logger,
    get_operation,
    get_columns,
    query_gpt,
    get_columns_join,
    get_prompt,
    get_filtered_functional_dependency,
    PromptTooLongError,
)

import re
from pathlib import Path
import shutil
import pandas as pd


# decided through parameters
len_id = 3
max_len_id = len_id
target_id = 1  # [11,18,22,25,62,10,16,31,38,5] # [18,2,32,33,96,16,27,78,91,18]
max_target_id = target_id
target_per = 25
is_perc = False
hint_source = p.hint_source
# 2
# target_length = int(max(3,10*0.9695545786258186))
# source_length = int(max(3,10*0.09828012752411708))

# 3
target_length = int(max(3, 10 * 0.31342417815924284))
source_length = int(max(3, 10 * 0.9682615757193975))

join_flag = 0
aggregate_flag = 0


use_intermediate_materialization = True

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


fd_flag = 1
token_limit = 120000
model = "gpt-4.1-mini"  # "gpt-4-turbo" # "gpt-3.5-turbo-16k" # "gpt-4-1-mini"


json_file_path = "data/chatgpt_github_ms.json"
log_dir = "logs-auto-suggest-llm-24-03"
main_folder = "autopipeline-benchmarks/github-pipelines"
source_space_dir = "source_space"

allowed_operation_list = [
    "JOIN",
    "UNION",
    "GROUP_BY/AGGREGATE",
    "PIVOT",
    "UNPIVOT",
    "NO_MORE_OPERATION",
]

q_count = {"total": 0, "in_task": 0}


def create_source_space(main_folder, len_id, target_id):
    # create source space
    source_space_path = Path(
        f"{main_folder}/{source_space_dir}/length{len_id}_{target_id}"
    )
    source_space_path.mkdir(exist_ok=True, parents=True)

    source_dir = Path(f"{main_folder}/length{len_id}_{target_id}")
    # Find all files matching the pattern "test{integer}.csv" in the source directory
    for file in source_dir.glob("test*.csv"):
        shutil.copy(file, source_space_path)


def get_operator(llm_client, operation_history):
    operation = None
    try:
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
            directory=main_folder,
            len_idx_target_idx=len_idx_target_idx,
            target_perc=target_per,
            is_perc=is_perc,
            target_length=target_length,
            source_length=source_length,
            source_space=1,
            fd_flag=fd_flag,
            hint_source=hint_source,
            use_intermediate_materialization=use_intermediate_materialization,
        )
    except PromptTooLongError as e:
        logger.info("Get Operator: Token Limit Exceeded")
    except Exception as e:
        raise e
    else:
        res = query_gpt(
            llm_client,
            model,
            prompt,
            q_count,
            logger,
            cost_summary,
            token_tracker,
            type="Ask For Operator",
        )
        operation = get_operation(res[0])
        if operation not in allowed_operation_list:
            raise Exception("Operation not in allowed list")

    return operation


def configure_operator(llm_client, operation):
    assert operation in allowed_operation_list
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
        try:
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
                directory=main_folder,
                len_idx_target_idx=len_idx_target_idx,
                target_perc=target_per,
                is_perc=is_perc,
                target_length=target_length,
                join_flag=join_flag,
                join_hints_truncate=join_hints_truncate,
                fd_flag=fd_flag,
                hint_source=hint_source,
                use_intermediate_materialization=use_intermediate_materialization,
            )
        except PromptTooLongError as e:
            logger.info("Configure operator: Token Limit Exceeded")

        except Exception as e:
            raise e

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


def materialize_chatgpt(llm_client, operation_history, save_path):
    error_str = ""
    for script_cnt in range(5):
        try:
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
                directory=main_folder,
                len_idx_target_idx=len_idx_target_idx,
                target_perc=target_per,
                is_perc=is_perc,
                target_length=target_length,
                error_string=error_str,
                source_space=1,
                fd_flag=fd_flag,
                hint_source=hint_source,
                save_path=save_path,
                use_intermediate_materialization=use_intermediate_materialization,
            )
        except PromptTooLongError as e:
            logger.info("Materialization: Token Limit Exceeded")

        except Exception as e:
            raise e

        res = query_gpt(
            llm_client,
            model,
            prompt,
            q_count,
            logger,
            cost_summary,
            token_tracker,
            type="Get Python Script",
        )
        print(res[0])
        script = res[0].split("```Python")[1].split("```")[0].strip()
        # print(script)

        response = execute_python(script)
        print(f"Python execution: {response}")
        error_str = error_str + response + "\n"
        # print(error_str)
        if response == "Success":
            return
    raise Exception("Materialization Failed")


def get_task(logger):
    task_list = get_test_cases_ids(
        json_file_path, len_id, max_len_id, target_id, max_target_id
    )
    task = task_list[0]

    logger.info("Started Experiment for : " + str(task))
    return task


class MaterializationCriteria:
    def __init__(self):
        self.ncalls = 0

    def __call__(self):
        self.ncalls += 1
        return True


def verify_result(target_file_location, ground_truth_location):

    df_our_response = pd.read_csv(target_file_location, low_memory=False)
    df_ground_truth = pd.read_csv(ground_truth_location, low_memory=False)
    df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)
    case_accuracy, is_correct, similarity_scores, validation_error = (
        compare_lists_matching(df_our_response, df_ground_truth)
    )
    log_str = f"Hard comparison, Task : {task} Case Accuracy : {case_accuracy}, is_correct : {is_correct}, similarity_score : {similarity_scores}"
    print(log_str)
    logger.info(log_str)
    # logger.info(validation_error)
    case_accuracy, is_correct, similarity_scores = compare_lists_matching_soft(
        df_our_response, df_ground_truth
    )
    log_str = f"Soft comparison, Task : {task} Case Accuracy : {case_accuracy}, is_correct : {is_correct}, similarity_score : {similarity_scores}"
    print(log_str)
    logger.info(log_str)
    compare_lists_matching_soft
    return is_correct


#################################################################################################################################

if __name__ == "__main__":
    create_source_space(main_folder, len_id, target_id)
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

    materialization_criteria = MaterializationCriteria()

    max_round = 6
    for _ in range(max_round):
        # first_get_operator
        op = get_operator(llm_client, operation_history)
        if op is None:
            print("No Operation Found, prompt is too long")
            continue
        if op == "NO_MORE_OPERATION":
            print("No More Operation")
            break

        configure_operator(llm_client, op)

        print(operation_history)

        if materialization_criteria():
            save_path = f"{main_folder}/{source_space_dir}/length{len_idx_target_idx}/materialize_step{materialization_criteria.ncalls}.csv"
            mat_table = materialize_chatgpt(llm_client, operation_history, save_path)

            is_correct = verify_result(
                save_path,
                f"{main_folder}/length{len_idx_target_idx}/target.csv",
            )
            if is_correct:
                print("Successful transformation")
                break
