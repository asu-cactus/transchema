# From the history 
    # First read the operation history from the excel file 
# recreate the python script and the result
    # 

import os
from pathlib import Path 
import pandas as pd
from test_scope import get_test_cases_ids
from auto_suggest_llm_util import create_logger, get_source, get_operation,get_join_hints,get_columns,get_groupby_aggregate_hints,get_source_with_location, cost_compare, query_gpt, get_columns_aggr,get_columns_join,get_prompt
from util.utils import get_test_info, execute_python,compare_lists_matching
import time
from llm.llm_models import TokenUsageTracker,LLMClient

# Read the Excel file
file_path_excel = 'experiment_results/Results_Refined/Results_Final_experiments_length4.ods'
excel_data = pd.read_excel(file_path_excel,engine='odf')

# Display the first few rows of the DataFrame
print(excel_data['task_name'], excel_data['op_history'])



json_file_path = "data/chatgpt_github_ms.json"
log_dir = "logs-auto-suggest-llm-data-recovery"
len_id = 4
max_len_id = 4
target_id = 28
max_target_id = 28
target_per = 10
is_perc = False
target_length = 3
main_folder = "autopipeline-benchmarks/github-pipelines"
model = 'gpt-4-turbo'
q_count = {'total' : 0, 'in_task' : 0}

allowed_operation_list = ['JOIN', 'UNION', 'GROUP_BY/AGGREGATE', 'PIVOT', 'UNPIVOT', 'NO_MORE_OPERATION']

task_list = get_test_cases_ids(json_file_path,  len_id, max_len_id, target_id, max_target_id)

logger = create_logger(log_dir,len_id, target_id,max_target_id)

for task in task_list :

    
    cost_summary = []
    start_time = time.time()
    token_tracker = TokenUsageTracker()
    cost_summary.append(token_tracker.cost_summary())
    llm_client = LLMClient(
                model=model, tracker=token_tracker, logger=logger
        )

    len_idx_target_idx = task[6:]


    if(task in excel_data['task_name'].values) :
        print(task, ' Exists')
        print('Operation History : ', excel_data.loc[excel_data['task_name'] == task, 'op_history'].values[0])
        operation_history = excel_data.loc[excel_data['task_name'] == task, 'op_history'].values[0]
    else :
        print(task, ' Does not exist')

    break_flag = 0
    if(break_flag == 0 and task in excel_data['task_name'].values) :
                    (target_data_name, target_data_schema, target_samples, file_count, source_data_name_list,
                source_data_schema_list, source_samples_list) = (
                get_test_info(json_file_path, len_idx_target_idx, main_folder))

                    # Generate Table and Compare
                    # ss = get_source_with_location(file_count, source_data_name_list,source_data_schema_list, source_samples_list, main_folder, len_idx_target_idx) 
                    target_file_location = '{main_folder}/length{len_idx_target_idx}/target_multisource_recovered.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
                    ground_truth_location = '{main_folder}/length{len_idx_target_idx}/target.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
                    python_code_location = '{main_folder}/length{len_idx_target_idx}/python_recovered.py'.format(main_folder = main_folder,len_idx_target_idx = len_idx_target_idx)
                    Path(target_file_location).touch()
                    # put this in a loop 
                    script_cnt = 0
                    error_str = ""
                    while(script_cnt < 5) :
                            prompt = get_prompt(prompt_type="python_script", max_tokens = False,model=model,allowed_operation_list=allowed_operation_list,
                                    operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema,
                                    target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                                    directory = main_folder, len_idx_target_idx = len_idx_target_idx, 
                                    source_samples_list = source_samples_list,
                                    target_perc = target_per, is_perc = is_perc, target_length = target_length, error_string = error_str,target_file_location = target_file_location)

                            if(prompt[0] == '-1') : 
                                            logger.info("Token Limit Exceeded")
                                            break_flag = 2
                                            break

                            res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker,type = "Get Python Script")
                            script = res[0].split("```Python")[1].split("```")[0].strip()
                            # print(script)
                            response = execute_python(script)
                            print(response)
                            error_str = error_str + response + '\n'
                            # print(error_str)
                            if(response == 'Success') : 
                                    break
                            script_cnt += 1

                    if(response == 'Success') : 
                            try : 
                                    # save python code 
                                    text_file = open(python_code_location, "w")
                                    text_file.write(script)
                                    text_file.close()

                                    df_our_response = pd.read_csv(target_file_location,low_memory=False)
                                    df_ground_truth = pd.read_csv(ground_truth_location,low_memory=False)
                                    df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)
                                    case_accuracy, is_correct, similarity_scores, validation_error = (
                                compare_lists_matching(df_our_response, df_ground_truth))
                                    print(case_accuracy,is_correct,similarity_scores,validation_error)
                                    logger.info("Task : "+task + " Case Accuracy : "+str(case_accuracy)+ ", is_correct : " + str(is_correct) +", similarity_score : "+ str(similarity_scores))
                            except :
                                    # logger.info(validation_error)
                                    print("Error in calculating accuracy.")
                    end_time = time.time()

    logger.info('''
            ******Task Summary**********
            Name : {task}
            Total queries made during this task : {q}
            Cost summary : {cost_summary}
            Tasks Used : {oh}
            Time elapsed : {time_elapsed}
            '''.format(task = str(task), q = str(q_count['in_task']), cost_summary = token_tracker.cost_summary(), oh = operation_history, time_elapsed = end_time - start_time))
