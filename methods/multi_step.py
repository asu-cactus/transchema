import time 
from llm.llm_models import TokenUsageTracker, LLMClient
from validation.hard_match import compare_lists_matching
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
import sys

def multi_step(args,length, id_, log_dir_, experiment_name,i_):
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


    fd_flag = args.fd_flag
    token_limit = args.token_limit
    model = args.model
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

    # log_dir = "logs-auto-suggest-llm-proof-bayesian"
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

    logger = create_logger("AUTOSUGGEST", log_dir, len_id, target_id, max_target_id)

    q_count = {"total": 0, "in_task": 0}

    # language = 'sql' #or 'python'

    ################## Run for each task ##################

    for task in task_list:

        q_count["in_task"] = 0

        logger.info("Started Experiment for : " + str(task))

        cost_summary = []

        start_time = time.time()
        token_tracker = TokenUsageTracker()
        cost_summary.append(token_tracker.cost_summary())
        # #print(cost_summary)

        len_idx_target_idx = task[6:]

        # #print(len_idx_target_idx)

        # Get the information of the target and source data

        (
            target_data_name,
            target_data_schema,
            target_samples,
            file_count,
            source_data_name_list,
            source_data_schema_list,
            source_samples_list,
        ) = get_test_info(json_file_path, len_idx_target_idx, main_folder, anon_flag)
        # added anon_flag to get_test_info() call

        # 0 to ask for operator and 1 for column and 2 to generate script
        toggle_operator = 0
        history_op = []
        history_elements = []
        operation_history = []

        llm_client = LLMClient(model=model, tracker=token_tracker, logger=logger)
        break_flag = 1

        while break_flag:

            prompt = get_prompt(prompt_type="get_next_operator", max_tokens = token_limit,model=model,allowed_operation_list=allowed_operation_list,
                            operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema,
                            target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                            directory = main_folder, len_idx_target_idx = len_idx_target_idx,
                            target_perc = target_per, is_perc = is_perc, target_length = target_length, source_length = source_length, hint_source = hint_source)
            if(prompt[0] == '-1') : 
                    logger.info("Token Limit Exceeded")
                    break_flag = 2
                    break
            # print(prompt)
            # # sys.exit()
            res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Ask For Operator")
            operation = get_operation(res[0])

            # sys.exit()
            # operation = 'JOIN'
            
            if operation == 'JOIN' :
                    # get join prompt 
                    prompt = get_prompt(prompt_type="join", max_tokens = token_limit,model=model,allowed_operation_list=allowed_operation_list,
                    operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema,
                    target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                    directory = main_folder, len_idx_target_idx = len_idx_target_idx, 
                    target_perc = target_per, is_perc = is_perc, target_length = target_length,join_flag = join_flag, join_hints_truncate = join_hints_truncate, hint_source = hint_source)
                    # sys.exit()
                    if(prompt[0] == '-1') : 
                            logger.info("Token Limit Exceeded")
                            break_flag = 2
                            break

                    # print(prompt[0])
                    # sys.exit()

                    res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Configure Join")
                    joined_columns = get_columns_join(res[0])
                    history_elements.append(joined_columns)
                    operation_history.append(operation + ' : ' + str(joined_columns))

                    # run llm and get join columns 
                    # add it to the history
                    pass 
            elif operation == 'GROUP_BY/AGGREGATE' :
                    # get group by prompt 
                    prompt = get_prompt(prompt_type="group_by_aggregate", max_tokens = token_limit,model=model,allowed_operation_list=allowed_operation_list,
                    operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema,
                    target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                    directory = main_folder, len_idx_target_idx = len_idx_target_idx, 
                    target_perc = target_per, is_perc = is_perc, target_length = target_length, aggregate_flag = aggregate_flag, aggregate_hints_truncate = aggregate_hints_truncate, hint_source = hint_source)
                    # sys.exit()
                    if(prompt[0] == '-1') : 
                            logger.info("Token Limit Exceeded")
                            break_flag = 2
                            break

                    # run llm and get group by column
                    # print(prompt[0]) 
                    # sys.exit()
                    res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Configure Group by/Aggergate")
                    # print(res[0])
                    # add it to the history
                    group_by_column = re.sub(r'```json\n|\n|```', '', res[0])
                    history_elements.append(res)
                    operation_history.append(group_by_column)
                    #operation_history.append(operation + ' : [ group_by : {group_by_column[0]}, aggregate : {group_by_column[1]}, aggregation_function : {group_by_column[2]} ]'.format(group_by_column = group_by_column))
                    pass
            elif operation == 'UNION' :
                    prompt = get_prompt(prompt_type="union", max_tokens = token_limit,model=model,allowed_operation_list=allowed_operation_list,
                    operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema,
                    target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                    directory = main_folder, len_idx_target_idx = len_idx_target_idx, 
                    target_perc = target_per, is_perc = is_perc, target_length = target_length,hint_source = hint_source)

                    if(prompt[0] == '-1') : 
                            logger.info("Token Limit Exceeded")
                            break_flag = 2
                            break

                    res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Configure Union")
                    # print(res[0])
                    tables_ = get_columns(res[0])
                    history_elements.append(tables_)
                    operation_history.append(operation + ' : ' + str(tables_))
                    pass
            elif operation == 'PIVOT' :
                    operation_history.append(operation)
                    pass 
            elif operation == 'UNPIVOT' :
                    operation_history.append(operation)
                    pass
            elif operation == 'NO_MORE_OPERATION' :
                    # generate python script 
                    # do similarity search 
                    # go to next 
                    break_flag = 0 
                    pass
            else :
                    pass

        #print(operation_history)

        if break_flag == 0:
            # Generate Table and Compare
            # ss = get_source_with_location(file_count, source_data_name_list,source_data_schema_list, source_samples_list, main_folder, len_idx_target_idx)
            target_file_location = "{main_folder}/length{len_idx_target_idx}/target_multisource.csv".format(
                main_folder=main_folder, len_idx_target_idx=len_idx_target_idx
            )
            ground_truth_location = (
                "{main_folder}/length{len_idx_target_idx}/target.csv".format(
                    main_folder=main_folder, len_idx_target_idx=len_idx_target_idx
                )
            )
            # put this in a loop
            script_cnt = 0
            error_str = ""
            while script_cnt < 5:
                prompt = get_prompt(prompt_type="python_script", max_tokens = token_limit,model=model,allowed_operation_list=allowed_operation_list,
                            operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema, 
                            target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                            directory = main_folder, len_idx_target_idx = len_idx_target_idx, 
                            target_perc = target_per, is_perc = is_perc, target_length = target_length, error_string = error_str,save_path = target_file_location, hint_source = hint_source)


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
                    type="Get Python Script",
                )
                pattern = re.compile(r"```Python(.*?)```", re.DOTALL | re.IGNORECASE)
                match = pattern.search(res[0])
                script = match.group(1).strip()
                print(script)
                response = execute_python(script)
                print(response)
                error_str = error_str + response + "\n"
                # #print(error_str)
                if response == "Success":
                    # sys.exit()
                    break
                script_cnt += 1

            if response == "Success":
                # save file here 
                # file_name
                if not os.path.exists(f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/script_archive"):
                    os.makedirs(f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/script_archive")
                with open(
                    f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/script_archive/{experiment_name}_{i_}.py",
                    "w",
                ) as file:
                    file.write(script)

                try : 
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
                    (
                        case_accuracy_,
                        is_correct_,
                        similarity_scores_
                    ) = compare_lists_matching_soft(df_our_response, df_ground_truth)
                    eps = 0.1
                    if case_accuracy_ < eps:
                        case_accuracy_ = 0
                    try:
                        (
                            case_accuracy,
                            is_correct,
                            similarity_scores,
                            validation_error,
                        ) = compare_lists_matching(df_our_response, df_ground_truth)
                        '''
                        print(
                            case_accuracy, is_correct, similarity_scores, validation_error
                        )
                        '''
                    except Exception as e:
                        print("".join(traceback.format_exc()))
                        is_correct = False
                    # calculate score 
                    score = calculate_score(df_ground_truth, df_our_response)
                except Exception as e:
                    print("".join(traceback.format_exc()))
                    case_accuracy = 0
                    is_correct = False
                    is_correct_ = False
                    case_accuracy_ = 0
                    score = 0
        op_hist_ = str(operation_history)
        end_time = time.time()

    # Only try to write the file if script was actually generated
    if script:
        with open(
            f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/python_recovered.py",
            "w",
        ) as file:
            file.write(script)
    case_path = f"{length}_{id_}"
    cost_data = token_tracker.cost_summary()  # This returns a dictionary
    total_cost = cost_data.get('total_cost', 0.0)  # Safely get total_cost with default
    time_elapsed = end_time - start_time
    #print("++++++++++++++++++++++++++++++++++++")
    #print(cost_data)
    #print("++++++++++++++++++++++++++++++++++++")
    ms_info = (
        is_correct,
        is_correct_,
        case_accuracy_,
        total_cost,  # Use the extracted total_cost value
        time_elapsed,
        score, 
        op_hist_
    )
    print(f"ms_info: {ms_info}")
    logger.info("Total Queries Made : {q}".format(q=q_count["total"]))
    
    return ms_info
