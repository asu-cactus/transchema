# Where to start 
# check if target_multisource is there 
# if yes,
#     then check the accuracy,
#     If the score is 1, then skip 
#     else get the critique prompt 
#         generate new python script based on this critique prompt 

# else 
#     using the operation history, generate the multisource file 
#     then follow the same process as if 

# What to put in critique prompt 
#     Comparision between FD mappings, keys and column mapping information as hint 

#     1. Ask llm to generate the python code that solves the FD mapping issue using a group by, count
    
#     2. Ask llm to find a way to generate the operator that should be used to satisfy FD mappings, if it gives group by, then check the number of the rows generated in the solution.
#         It may not be able to get the generate the count but it should generate the group by.


import os
from pathlib import Path 
import re
import pandas as pd
from test_scope import get_test_cases_ids
from auto_suggest_llm_util import create_logger, get_source, get_operation,get_join_hints,get_columns,get_groupby_aggregate_hints,get_source_with_location, cost_compare, query_gpt, get_columns_aggr,get_columns_join,get_prompt,calculate_score
from util.utils import get_test_info, execute_python,compare_lists_matching
import time
from llm.llm_models import TokenUsageTracker,LLMClient
import auto_suggest_llm_prompts as prt
from quality.quality import analyze_functional_dependencies,data_profiling,data_summary

json_file_path = "data/chatgpt_github_ms.json"
log_dir = "logs-auto-suggest-llm-critique"
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
error_margin = 0.1

# read excel file for operation history 
# Read the Excel file
file_path_excel = 'experiment_results/Results_Refined/Results_Final_experiments_length4.ods'
excel_data = pd.read_excel(file_path_excel,engine='odf')

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

    if(task in excel_data['task_name'].values) :
        print(task, ' Exists')
        print('Operation History : ', excel_data.loc[excel_data['task_name'] == task, 'op_history'].values[0])
        operation_history = excel_data.loc[excel_data['task_name'] == task, 'op_history'].values[0]
    else :
        logger.info(task, ' Does not exist')
        continue

    len_idx_target_idx = task[6:]

    (target_data_name, target_data_schema, target_samples, file_count, source_data_name_list,
                source_data_schema_list, source_samples_list) = (
                get_test_info(json_file_path, len_idx_target_idx, main_folder))

    source_information = get_source(file_count, source_data_name_list,
                source_data_schema_list, source_samples_list)

    python_script_location = '{main_folder}/length{len_idx_target_idx}/python_recovered.py'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx) 
    ground_truth_location = '{main_folder}/length{len_idx_target_idx}/target.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
    df_ground_truth = pd.read_csv(ground_truth_location,low_memory=False)
    df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)
    try : 
        target_file_location = '{main_folder}/length{len_idx_target_idx}/target_multisource_recovered.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
        df_our_response = pd.read_csv(target_file_location,low_memory=False)
    except : 
        logger.info("Python Error Case.")
        continue

    fd_score, key_score, mapping_score = calculate_score(df_ground_truth, df_our_response)

    single_analysis, multi_analysis, dependencies = data_profiling(df_ground_truth)
    summary = data_summary(single_analysis, multi_analysis, dependencies)

    script_cnt = 5 # 5 attempts

    # read transformed data schema and transformed data examples 
    transformed_schema = list(df_our_response.columns)
    transformed_data_examples = df_our_response.head(min(3,df_our_response.shape[0])).values.tolist()
    

    while(1-fd_score > error_margin or 1-key_score > error_margin or 1-mapping_score > error_margin) : 
        
        # get python script 
        with open(python_script_location) as f : python_code = f.read()
        target_file_location = '{main_folder}/length{len_idx_target_idx}/target_multisource_critique.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)

        prompt = prt.get_critique_prompt(allowed_operation_list=allowed_operation_list,operation_history=operation_history,target_data_schema=target_data_schema,
                        target_samples=target_samples,file_count=file_count, source_information=source_information, 
                        target_file_location=target_file_location, error_string="", summary=summary, python_code = python_code,
                        transformed_data_schema = transformed_schema, transformed_samples = transformed_data_examples)
        res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Critique Query")

        pattern = re.compile(r"```Python(.*?)```", re.DOTALL)
        match = pattern.search(res[0])
        script = match.group(1).strip()

        # print(script)
        response = execute_python(script)
        print(response)
        # error_str = error_str + response + '\n'
        # print(error_str)
        if(response == 'Success') : 
                target_file_location = '{main_folder}/length{len_idx_target_idx}/target_multisource_critique.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
                df_our_response = pd.read_csv(target_file_location,low_memory=False)
                fd_score, key_score, mapping_score = calculate_score(df_ground_truth, df_our_response)
                logger.info("FD Score : " + str(1-fd_score) + " Key Score : " + str(1-key_score) + " Mapping Score : " +  str(1-mapping_score))
        script_cnt -= 1
        if(script_cnt <= 0) : break

    # calculate accuracy
    case_accuracy, is_correct, similarity_scores, validation_error = (
        compare_lists_matching(df_our_response, df_ground_truth))
    print(case_accuracy,is_correct,similarity_scores,validation_error)
    logger.info("Task : "+task + " Case Accuracy : "+str(case_accuracy)+ ", is_correct : " + str(is_correct) +", similarity_score : "+ str(similarity_scores))

    end_time = time.time()

    logger.info('''
            ******Task Summary**********
            Name : {task}
            Total queries made during this task : {q}
            Cost summary : {cost_summary}
            Tasks Used : {oh}
            Time elapsed : {time_elapsed}
            '''.format(task = str(task), q = str(q_count['in_task']), cost_summary = token_tracker.cost_summary(), oh = operation_history, time_elapsed = end_time - start_time))


    


