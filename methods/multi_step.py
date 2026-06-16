import time
from dataclasses import dataclass, field
from llm.llm_models import TokenUsageTracker, LLMClient
from validation.hard_match import is_column_numerical, compare_lists_matching, compare_tables_matching
from validation.soft_match import compare_lists_matching_soft
from util.utils import get_test_info, execute_python, make_test_validation_script
from test_scope import get_test_cases_ids
from auto_suggest_llm_util import (
    get_prompt,
    query_gpt,
    get_operation,
    get_columns,
    get_columns_join,
)
from eval_score_value_based import value_based_relative_csv_score_timed
from judges import build_nl_score_interpretation

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
    static_hints: bool
    past_context: str = ""
    rag_hints: str = ""
    intermediate_scores: dict = field(default_factory=dict)
    data_split: str = "test"


def get_python_response(operation_history, break_flag, csv_save_path, config: Config, intermediate_scores=None, nth_intermediate_step: int = 0, is_final: bool = False):
    logger = config.logger
    llm_client = config.llm_client
    past_context = getattr(config, "past_context", "")
    intermediate_scores = intermediate_scores or {}

    max_trails = 5
    error_str = ""
    script = ""
    response = ""
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
            static_hints=config.static_hints,
            past_context=past_context,
            rag_hints=getattr(config, "rag_hints", ""),
            intermediate_scores=intermediate_scores,
            nth_intermediate_step=nth_intermediate_step,
            source_length=config.source_length,
            is_final=is_final,
            data_split=getattr(config, "data_split", "test"),
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
    # create source space (derive from main_folder so benchmark selector works)
    _source_space_dir = f"{main_folder}/intermediate_space"
    source_space_path = Path(f"{_source_space_dir}/length{len_id}_{target_id}")
    source_space_path.mkdir(exist_ok=True, parents=True)

    source_dir = Path(f"{main_folder}/length{len_id}_{target_id}")
    # Find all files matching the pattern "test{integer}.csv" in the source directory
    for file in source_dir.glob("*"):
        if file.is_file():  # Skip directories
            shutil.copy(file, source_space_path)
    return _source_space_dir


_REASONING_INSTRUCTION = (
    "\n- Please include a brief explanation of your reasoning for this choice."
)


def _build_op_history_entry(granularity, summary_str, ask_prompt, ask_response,
                             config_prompt=None, config_response=None):
    """Format an operation_history entry based on memory granularity.

    summary  -> compact extracted string (current behaviour)
    response -> full LLM responses only (no prompts)
    qa       -> full prompt + response for each step
    """
    if granularity == "summary":
        return summary_str
    lines = ["[Ask For Operator]"]
    if granularity == "qa":
        lines.append(f"  Prompt: {ask_prompt}")
    lines.append(f"  Response: {ask_response}")
    if config_response is not None:
        lines.append("[Configure]")
        if granularity == "qa":
            lines.append(f"  Prompt: {config_prompt}")
        lines.append(f"  Response: {config_response}")
    return "\n".join(lines)


def multi_step(args, length, id_, log_dir_, experiment_name, i_, past_context_str="", token_tracker=None, budget=None):
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
    cost_summary = []
    start_time = time.time()
    if token_tracker is None:
        token_tracker = TokenUsageTracker()
    script = ""
    op_hist_ = ""
    hint_source = args.hint_source
    len_id = length
    validate_fn = compare_tables_matching if getattr(args, "validation", "hard_match") == "autopipeline" else compare_lists_matching
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
    static_hints = args.static_hints
    # Benchmark selector: github | monteprep
    benchmark = getattr(args, "benchmark", "github")
    main_folder = "autopipeline-benchmarks/monteprep-pipelines" if benchmark == "monteprep" else "autopipeline-benchmarks/github-pipelines"
    source_space_dir = f"{main_folder}/intermediate_space"
    path_to_files = f"{main_folder}/length{length}_{id_}/"
    data_split = getattr(args, "data_split", "test")
    # Counting files starting with data_split prefix in this subfolder (root only, no subdirs)
    file_count = sum(
        1
        for file in os.listdir(path_to_files)
        if os.path.isfile(os.path.join(path_to_files, file))
        if file.startswith(data_split)
    )

    if args.intermediate_materialization:
        interm_space_dir = create_intermediate_space(main_folder, len_id, target_id)
    # print(file_count)

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
    directory = source_space_dir if args.intermediate_materialization else main_folder

    # language = 'sql' #or 'python'

    ################## Run for each task ##################

    for task in task_list:  # Note: this is always only one task

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
            static_hints=static_hints,
            past_context=past_context_str,
            data_split=data_split,
        )

        history_elements = []
        operation_history = []
        break_flag = 1
        granularity = getattr(args, "memory_granularity", "summary")
        intermediate_scores = {}  # {step: (true_combined_score, nl_score)}

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
                nth_intermediate_step=step + 1 if args.intermediate_materialization else 0,
                static_hints=static_hints,
                past_context=past_context_str,
                intermediate_scores=intermediate_scores,
                data_split=data_split,
            )
            if prompt[0] == "-1":
                logger.info("Token Limit Exceeded")
                break_flag = 2
                break
            if granularity in ("response", "qa"):
                prompt += _REASONING_INSTRUCTION
            ask_prompt = prompt
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
            ask_response = res[0]
            operation = get_operation(ask_response)
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
                        step + 1 if args.intermediate_materialization else 0
                    ),
                    static_hints=static_hints,
                    past_context=past_context_str,
                    data_split=data_split,
                )

                if prompt[0] == "-1":
                    logger.info("Token Limit Exceeded")
                    break_flag = 2
                    break

                if granularity in ("response", "qa"):
                    prompt += _REASONING_INSTRUCTION
                config_prompt = prompt
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
                config_response = res[0]
                joined_columns = get_columns_join(config_response)
                history_elements.append(joined_columns)
                operation_history.append(_build_op_history_entry(
                    granularity, operation + " : " + str(joined_columns),
                    ask_prompt, ask_response, config_prompt, config_response,
                ))

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
                        step + 1 if args.intermediate_materialization else 0
                    ),
                    static_hints=static_hints,
                    past_context=past_context_str,
                    data_split=data_split,
                )
                if prompt[0] == "-1":
                    logger.info("Token Limit Exceeded")
                    break_flag = 2
                    break

                if granularity in ("response", "qa"):
                    prompt += _REASONING_INSTRUCTION
                config_prompt = prompt
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
                config_response = res[0]
                # add it to the history
                group_by_column = re.sub(r"```json\n|\n|```", "", config_response)
                history_elements.append(res)
                operation_history.append(_build_op_history_entry(
                    granularity, group_by_column,
                    ask_prompt, ask_response, config_prompt, config_response,
                ))
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
                        step + 1 if args.intermediate_materialization else 0
                    ),
                    static_hints=static_hints,
                    past_context=past_context_str,
                    data_split=data_split,
                )

                if prompt[0] == "-1":
                    logger.info("Token Limit Exceeded")
                    break_flag = 2
                    break

                if granularity in ("response", "qa"):
                    prompt += _REASONING_INSTRUCTION
                config_prompt = prompt
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
                config_response = res[0]
                tables_ = get_columns(config_response)
                history_elements.append(tables_)
                operation_history.append(_build_op_history_entry(
                    granularity, operation + " : " + str(tables_),
                    ask_prompt, ask_response, config_prompt, config_response,
                ))
                pass
            elif operation == "PIVOT":
                operation_history.append(_build_op_history_entry(
                    granularity, operation, ask_prompt, ask_response,
                ))
                pass
            elif operation == "UNPIVOT":
                operation_history.append(_build_op_history_entry(
                    granularity, operation, ask_prompt, ask_response,
                ))
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
            if args.intermediate_materialization and break_flag != 0:
                csv_save_path = f"{interm_space_dir}/length{len_idx_target_idx}/intermediate_step{step}.csv"
                script, response, break_flag = get_python_response(
                    operation_history, break_flag, csv_save_path, config, intermediate_scores,
                    nth_intermediate_step=step,
                )
                if os.path.exists(csv_save_path):
                    try:
                        df_interm = pd.read_csv(csv_save_path, low_memory=False)
                        df_gt = pd.read_csv(ground_truth_location, low_memory=False)
                        df_gt.drop(columns=df_gt.columns[0], axis=1, inplace=True)
                        _, col_ratio_s, _, fd_f1_s, true_combined_s, debug_dict_s = value_based_relative_csv_score_timed(df_interm, df_gt)
                        nl_score_s = build_nl_score_interpretation(fd_f1_s, col_ratio_s, true_combined_s, debug_dict_s)
                        intermediate_scores[step] = (true_combined_s, nl_score_s)
                    except Exception as e:
                        logger.warning(f"Intermediate score computation failed at step {step}: {e}\n{traceback.format_exc()}")
            print(f"finished step {step}")

        # print(operation_history)

        if break_flag == 0:
            # Generate Table and Compare
            # ss = get_source_with_location(file_count, source_data_name_list,source_data_schema_list, source_samples_list, main_folder, len_idx_target_idx)

            # put this in a loop
            script, response, break_flag = get_python_response(
                operation_history, break_flag, target_file_location, config,
                intermediate_scores=intermediate_scores,
                nth_intermediate_step=step,
                is_final=True,
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
                        ) = validate_fn(df_our_response, df_ground_truth)
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
                            ) = validate_fn(
                                sorted_df_our_response, sorted_df_ground_truth
                            )
                        else:
                            _, col_ratio_val, _, fd_f1_val, score, debug_dict_val = value_based_relative_csv_score_timed(df_our_response, df_ground_truth)
                    except Exception as e:
                        print("".join(traceback.format_exc()))
                        is_correct = False
                except Exception as e:
                    print("".join(traceback.format_exc()))
                    case_accuracy = 0
                    is_correct = False
                    score = 0
        # Two-phase validation: score on training output, is_correct on test output
        if data_split == "training" and script:
            test_script = make_test_validation_script(script)
            test_output = f"{main_folder}/length{len_idx_target_idx}/target_multisource_test_val.csv"
            print("[two-phase ms] executing test-data script for is_correct validation...")
            test_exec = execute_python(test_script)
            if test_exec == "Success" and os.path.exists(test_output):
                try:
                    df_test = pd.read_csv(test_output, low_memory=False)
                    df_gt_test = pd.read_csv(ground_truth_location, low_memory=False)
                    df_gt_test.drop(columns=df_gt_test.columns[0], axis=1, inplace=True)
                    _, test_is_correct, _, _ = validate_fn(df_test, df_gt_test)
                    print(f"[two-phase ms] is_correct: training={is_correct} → test={test_is_correct}")
                    is_correct = test_is_correct
                except Exception:
                    print(f"[two-phase ms] test validation failed:\n{traceback.format_exc()}")
            else:
                print(f"[two-phase ms] test exec={test_exec}, output_exists={os.path.exists(test_output)}")

        op_hist_ = str(operation_history)
    end_time = time.time()

    # Only try to write the file if script was actually generated
    if script:
        recovered_path = f"{main_folder}/length{length}_{id_}/python_recovered.py"
        with open(recovered_path, "w") as file:
            file.write(script)
        print(f"[multi_step] python_recovered.py written: {recovered_path}")
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

    return ms_info, (df_our_response, fd_f1_val, col_ratio_val, score, debug_dict_val)
