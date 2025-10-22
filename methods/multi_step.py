import time
from dataclasses import dataclass
from llm.llm_models import TokenUsageTracker, LLMClient
from validation.hard_match import is_column_numerical, compare_lists_matching
from validation.soft_match import compare_lists_matching_soft
from util.utils import get_test_info, execute_python
from test_scope import get_test_cases_ids
from auto_suggest_llm_util import (
    calculate_score,
    get_prompt,
    query_gpt,
    get_operation,
    get_columns,
    get_columns_join,
)

from log_util.log_util import create_logger

# import parameters as p
import re
import pandas as pd
import os
import traceback
from pathlib import Path
import shutil

main_folder = "autopipeline-benchmarks/github-pipelines"
source_space_dir = f"{main_folder}/intermediate_space"


allowed_operation_list = [
    "JOIN",
    "UNION",
    "GROUP_BY/AGGREGATE",
    "PIVOT",
    "UNPIVOT",
    "NO_MORE_OPERATION",
]


@dataclass
class Config:
    target_data_name: str
    target_data_schema: str
    target_data_schema_with_types: str
    target_samples: str
    file_count: int
    source_data_name_list: list
    source_data_schema_list: list
    directory: str
    len_idx_target_idx: str
    target_perc: float
    is_perc: bool
    target_length: int
    source_length: int
    fd_flag: bool
    hint_source: str
    llm_client: LLMClient
    q_count: dict
    logger: any
    cost_summary: list
    token_tracker: TokenUsageTracker
    model: str
    token_limit: int


def get_python_response(operation_history, break_flag, csv_save_path, config: Config):
    logger = config.logger
    llm_client = config.llm_client

    max_trails = 5
    error_str = ""
    for _ in range(max_trails):
        prompt = get_prompt(
            prompt_type="python_script",
            max_tokens=config.token_limit,
            model=config.model,
            allowed_operation_list=allowed_operation_list,
            operation_history=operation_history,
            target_data_name=config.target_data_name,
            target_data_schema=config.target_data_schema,
            target_data_schema_with_types=config.target_data_schema_with_types,
            target_samples=config.target_samples,
            file_count=config.file_count,
            source_data_name_list=config.source_data_name_list,
            source_data_schema_list=config.source_data_schema_list,
            directory=config.directory,
            len_idx_target_idx=config.len_idx_target_idx,
            target_perc=config.target_perc,
            is_perc=config.is_perc,
            target_length=config.target_length,
            error_string=error_str,
            csv_save_path=csv_save_path,
            hint_source=config.hint_source,
        )

        if prompt[0] == "-1":
            logger.info("Token Limit Exceeded")
            break_flag = 2
            break

        res = query_gpt(
            llm_client,
            config.model,
            prompt,
            config.q_count,
            logger,
            config.cost_summary,
            config.token_tracker,
            type="Get Python Script",
        )
        pattern = re.compile(r"```Python(.*?)```", re.DOTALL | re.IGNORECASE)
        match = pattern.search(res[0])
        try:
            script = match.group(1).strip()
            response = execute_python(script)
            error_str = error_str + response + "\n"
            if response == "Success":
                break
        except Exception as e:
            print("".join(traceback.format_exc()))
            response = ""
            error_str = error_str + "No valid response from LLM.\n"
    else:
        print(f"Exceed {max_trails} trails, Materialization Failed")
    return script, response, break_flag


def create_intermediate_space(main_folder, len_id, target_id):
    # create source space

    source_space_path = Path(f"{source_space_dir}/length{len_id}_{target_id}")
    source_space_path.mkdir(exist_ok=True, parents=True)

    source_dir = Path(f"{main_folder}/length{len_id}_{target_id}")
    # Find all files matching the pattern "test{integer}.csv" in the source directory
    for file in source_dir.glob("*"):
        if file.is_file():  # Skip directories
            shutil.copy(file, source_space_path)
    return source_space_dir


def multi_step(args, length, id_, log_dir_, experiment_name, i_):
    # Initialize required variables
    case_path = f"{length}_{id_}"
    is_correct = False
    is_correct_ = False
    case_accuracy_ = 0
    score = 0
    case_accuracy = 0
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
    path_to_files = f"{main_folder}/length{length}_{id_}/"
    # Counting files starting with 'test' in this subfolder
    file_count = sum(
        1
        for _, _, files in os.walk(path_to_files)
        for file in files
        if file.startswith("test")
    )

    if args.intermediate_materialization:
        interm_space_dir = create_intermediate_space(main_folder, len_id, target_id)
    # print(file_count)

    if file_count > 1:
        json_file_path = "data/chatgpt_github_ms.json"
    else:
        json_file_path = "data/chatgpt_github_ss.json"

    log_dir = log_dir_

    task_list = get_test_cases_ids(
        json_file_path, len_id, max_len_id, target_id, max_target_id
    )

    logger = create_logger("AUTOSUGGEST", log_dir, len_id, target_id, max_target_id)

    q_count = {"total": 0, "in_task": 0}

    # Create configuration for LLM calls
    directory = source_space_dir if args.intermediate_materialization else main_folder

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

        target_file_location = (
            f"{main_folder}/length{len_idx_target_idx}/target_multisource.csv"
        )
        ground_truth_location = f"{main_folder}/length{len_idx_target_idx}/target.csv"
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
        )

        history_elements = []
        operation_history = []
        break_flag = 1

        step = 0
        while break_flag:

            prompt = get_prompt(
                prompt_type="get_next_operator",
                max_tokens=token_limit,
                model=model,
                allowed_operation_list=allowed_operation_list,
                operation_history=operation_history,
                target_data_name=target_data_name,
                target_data_schema=target_data_schema,
                target_samples=target_samples,
                target_data_schema_with_types=target_data_schema_with_types,
                file_count=file_count,
                source_data_name_list=source_data_name_list,
                source_data_schema_list=source_data_schema_list,
                directory=directory,
                len_idx_target_idx=len_idx_target_idx,
                target_perc=target_per,
                is_perc=is_perc,
                target_length=target_length,
                source_length=source_length,
                hint_source=hint_source,
                few_shot=few_shot,
                nth_intermediate_step=step if args.intermediate_materialization else 0,
            )
            if prompt[0] == "-1":
                logger.info("Token Limit Exceeded")
                break_flag = 2
                break
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
            print(operation)

            # operation = 'JOIN'

            if operation == "JOIN":
                # get join prompt
                prompt = get_prompt(
                    prompt_type="join",
                    max_tokens=token_limit,
                    model=model,
                    allowed_operation_list=allowed_operation_list,
                    operation_history=operation_history,
                    target_data_name=target_data_name,
                    target_data_schema=target_data_schema,
                    target_data_schema_with_types=target_data_schema_with_types,
                    target_samples=target_samples,
                    file_count=file_count,
                    source_data_name_list=source_data_name_list,
                    source_data_schema_list=source_data_schema_list,
                    directory=directory,
                    len_idx_target_idx=len_idx_target_idx,
                    target_perc=target_per,
                    is_perc=is_perc,
                    target_length=target_length,
                    join_flag=join_flag,
                    join_hints_truncate=join_hints_truncate,
                    hint_source=hint_source,
                    few_shot=few_shot,
                    nth_intermediate_step=(
                        step if args.intermediate_materialization else 0
                    ),
                )

                if prompt[0] == "-1":
                    logger.info("Token Limit Exceeded")
                    break_flag = 2
                    break

                res = query_gpt(
                    llm_client,
                    model,
                    prompt,
                    q_count,
                    logger,
                    cost_summary,
                    token_tracker,
                    type="Configure Join",
                )
                joined_columns = get_columns_join(res[0])
                history_elements.append(joined_columns)
                operation_history.append(operation + " : " + str(joined_columns))

                # run llm and get join columns
                # add it to the history
                pass
            elif operation == "GROUP_BY/AGGREGATE":
                # get group by prompt
                prompt = get_prompt(
                    prompt_type="group_by_aggregate",
                    max_tokens=token_limit,
                    model=model,
                    allowed_operation_list=allowed_operation_list,
                    operation_history=operation_history,
                    target_data_name=target_data_name,
                    target_data_schema=target_data_schema,
                    target_data_schema_with_types=target_data_schema_with_types,
                    target_samples=target_samples,
                    file_count=file_count,
                    source_data_name_list=source_data_name_list,
                    source_data_schema_list=source_data_schema_list,
                    directory=directory,
                    len_idx_target_idx=len_idx_target_idx,
                    target_perc=target_per,
                    is_perc=is_perc,
                    target_length=target_length,
                    aggregate_flag=aggregate_flag,
                    aggregate_hints_truncate=aggregate_hints_truncate,
                    hint_source=hint_source,
                    few_shot=few_shot,
                    nth_intermediate_step=(
                        step if args.intermediate_materialization else 0
                    ),
                )
                if prompt[0] == "-1":
                    logger.info("Token Limit Exceeded")
                    break_flag = 2
                    break

                # run llm and get group by column
                res = query_gpt(
                    llm_client,
                    model,
                    prompt,
                    q_count,
                    logger,
                    cost_summary,
                    token_tracker,
                    type="Configure Group by/Aggergate",
                )
                # add it to the history
                group_by_column = re.sub(r"```json\n|\n|```", "", res[0])
                history_elements.append(res)
                operation_history.append(group_by_column)
                # operation_history.append(operation + ' : [ group_by : {group_by_column[0]}, aggregate : {group_by_column[1]}, aggregation_function : {group_by_column[2]} ]'.format(group_by_column = group_by_column))
                pass
            elif operation == "UNION":
                prompt = get_prompt(
                    prompt_type="union",
                    max_tokens=token_limit,
                    model=model,
                    allowed_operation_list=allowed_operation_list,
                    operation_history=operation_history,
                    target_data_name=target_data_name,
                    target_data_schema=target_data_schema,
                    target_data_schema_with_types=target_data_schema_with_types,
                    target_samples=target_samples,
                    file_count=file_count,
                    source_data_name_list=source_data_name_list,
                    source_data_schema_list=source_data_schema_list,
                    directory=directory,
                    len_idx_target_idx=len_idx_target_idx,
                    target_perc=target_per,
                    is_perc=is_perc,
                    target_length=target_length,
                    hint_source=hint_source,
                    few_shot=few_shot,
                    nth_intermediate_step=(
                        step if args.intermediate_materialization else 0
                    ),
                )

                if prompt[0] == "-1":
                    logger.info("Token Limit Exceeded")
                    break_flag = 2
                    break

                res = query_gpt(
                    llm_client,
                    model,
                    prompt,
                    q_count,
                    logger,
                    cost_summary,
                    token_tracker,
                    type="Configure Union",
                )
                tables_ = get_columns(res[0])
                history_elements.append(tables_)
                operation_history.append(operation + " : " + str(tables_))
                pass
            elif operation == "PIVOT":
                operation_history.append(operation)
                pass
            elif operation == "UNPIVOT":
                operation_history.append(operation)
                pass
            elif operation == "NO_MORE_OPERATION" or operation == "" or step > 15:
                # generate python script
                # do similarity search
                # go to next
                break_flag = 0
                pass
            else:
                pass

            # Materialize the intermediate table here itself
            step += 1
            if args.intermediate_materialization:
                csv_save_path = f"{interm_space_dir}/length{len_idx_target_idx}/intermediate_step{step}.csv"
                script, response, break_flag = get_python_response(
                    operation_history, break_flag, csv_save_path, config
                )
            print(f"finished step {step}")

        # print(operation_history)

        if break_flag == 0:
            # Generate Table and Compare
            # ss = get_source_with_location(file_count, source_data_name_list,source_data_schema_list, source_samples_list, main_folder, len_idx_target_idx)

            # put this in a loop
            script, response, break_flag = get_python_response(
                operation_history, break_flag, target_file_location, config
            )

            if response == "Success":
                # save file here
                # file_name
                if not os.path.exists(
                    f"{main_folder}/length{length}_{id_}/script_archive"
                ):
                    os.makedirs(f"{main_folder}/length{length}_{id_}/script_archive")
                with open(
                    f"{main_folder}/length{length}_{id_}/script_archive/{experiment_name}_{i_}.py",
                    "w",
                ) as file:
                    file.write(script)

                try:
                    # name_of_experiment_pass_1
                    df_our_response = pd.read_csv(
                        target_file_location, low_memory=False
                    )
                    df_ground_truth = pd.read_csv(
                        ground_truth_location, low_memory=False
                    )
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
                        if (
                            is_correct == False
                            and len(shared_columns) > 0
                            and len(df_our_response) == len(df_ground_truth)
                        ):
                            print(
                                "TRY IGNORING COLUMN HEADERS AND SORTING COLUMNS FOR BETTER COMPARISON:"
                            )
                            sorted_df_our_response = df_our_response.sort_values(
                                by=shared_columns
                            )
                            sorted_df_ground_truth = df_ground_truth.sort_values(
                                by=shared_columns
                            )
                            new_header_our_response = []
                            for col in sorted_df_our_response.columns:
                                if "float" in str(sorted_df_our_response[col].dtype):
                                    print("is float")
                                    first_three_values = (
                                        sorted_df_our_response[col].head(3).astype(int)
                                    )
                                else:
                                    print("is not float")
                                    first_three_values = sorted_df_our_response[
                                        col
                                    ].head(3)
                                concatenated_header = (
                                    str(first_three_values.iloc[0])
                                    + "-"
                                    + str(first_three_values.iloc[1])
                                    + "-"
                                    + str(first_three_values.iloc[2])
                                )
                                print(concatenated_header)
                                new_header_our_response.append(concatenated_header)
                            sorted_df_our_response.columns = new_header_our_response
                            new_header_ground_truth = []
                            for col in sorted_df_ground_truth.columns:
                                if "float" in str(sorted_df_ground_truth[col].dtype):
                                    print("is float")
                                    first_three_values = (
                                        sorted_df_ground_truth[col].head(3).astype(int)
                                    )
                                else:
                                    print("is not float")
                                    first_three_values = sorted_df_ground_truth[
                                        col
                                    ].head(3)
                                concatenated_header = (
                                    str(first_three_values.iloc[0])
                                    + "-"
                                    + str(first_three_values.iloc[1])
                                    + "-"
                                    + str(first_three_values.iloc[2])
                                )
                                print(concatenated_header)
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
        op_hist_ = str(operation_history)
    end_time = time.time()

    # Only try to write the file if script was actually generated
    if script:
        with open(
            f"{main_folder}/length{length}_{id_}/python_recovered.py",
            "w",
        ) as file:
            file.write(script)
    case_path = f"{length}_{id_}"
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

    return ms_info
