from test_scope import get_test_cases_ids
from llm.llm_models import TokenUsageTracker,LLMClient
from util.utils import get_test_info, execute_python,compare_lists_matching
import time
import auto_suggest_llm_prompts as prt
from auto_suggest_llm_util import create_logger, get_source, get_operation,get_join_hints,get_columns,get_groupby_aggregate_hints,get_source_with_location, cost_compare, query_gpt, get_columns_aggr,get_columns_join,get_prompt
import pandas as pd
import re
import sys
from pathlib import Path
import os


# decided through parameters
len_id = int(sys.argv[1])
max_len_id = int(sys.argv[2])
target_id = int(sys.argv[3])
max_target_id = int(sys.argv[4])
target_per = int(sys.argv[5])
is_perc = bool(int(sys.argv[6]))  # Convert string to int first, then to bool
target_length = int(sys.argv[7])
source_length = int(sys.argv[8])
join_flag = int(sys.argv[9])
aggregate_flag = int(sys.argv[10])

# Convert comma-separated strings back to lists of floats
join_hints_truncate = list(map(float, sys.argv[11].split(',')))
aggregate_hints_truncate = list(map(float, sys.argv[12].split(',')))

fd_flag = int(sys.argv[13])
token_limit = int(sys.argv[14])
model = sys.argv[15]
    


json_file_path = "data/chatgpt_github_ms.json"
log_dir = "logs-auto-suggest-llm-bayesian-parameter-optimization-cluster-0"
main_folder = "autopipeline-benchmarks/github-pipelines"

allowed_operation_list = ['JOIN', 'UNION', 'GROUP_BY/AGGREGATE', 'PIVOT', 'UNPIVOT', 'NO_MORE_OPERATION']

task_list = get_test_cases_ids(json_file_path,  len_id, max_len_id, target_id, max_target_id)

logger = create_logger(log_dir,len_id, target_id,max_target_id)

q_count = {'total' : 0, 'in_task' : 0}

#language = 'sql' #or 'python'

################## Run for each task ##################

for task in task_list :
        
        q_count['in_task'] = 0

        logger.info("Started Experiment for : "+str(task))

        cost_summary = []

        start_time = time.time()
        token_tracker = TokenUsageTracker()
        cost_summary.append(token_tracker.cost_summary())
        # print(cost_summary)

        len_idx_target_idx = task[6:]

        # print(len_idx_target_idx)

        # Get the information of the target and source data

        (target_data_name, target_data_schema, target_samples, file_count, source_data_name_list,
                source_data_schema_list, source_samples_list) = (
                get_test_info(json_file_path, len_idx_target_idx, main_folder))


        # 0 to ask for operator and 1 for column and 2 to generate script
        toggle_operator = 0
        history_op = []
        history_elements = []
        operation_history = []

        llm_client = LLMClient(
                model=model, tracker=token_tracker, logger=logger
        )
        # source_information = get_source(file_count, source_data_name_list,
                # source_data_schema_list, source_samples_list, main_directory, len_idx_target_idx, sample_length)
        break_flag = 1

        while(break_flag) :

                # print(operation_history)

                prompt = get_prompt(prompt_type="get_next_operator", max_tokens = token_limit,model=model,allowed_operation_list=allowed_operation_list,
                                operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema,
                                target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                                directory = main_folder, len_idx_target_idx = len_idx_target_idx,
                                target_perc = target_per, is_perc = is_perc, target_length = target_length, source_length = source_length, fd_flag = fd_flag)
                if(prompt[0] == '-1') : 
                        logger.info("Token Limit Exceeded")
                        break_flag = 2
                        break
                # print(prompt)
                # sys.exit()
                res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Ask For Operator")
                operation = get_operation(res[0])
                # sys.exit()
                
                if operation == 'JOIN' :
                        # get join prompt 
                        prompt = get_prompt(prompt_type="join", max_tokens = token_limit, model=model, allowed_operation_list=allowed_operation_list,
                        operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema,
                        target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                        directory = main_folder, len_idx_target_idx = len_idx_target_idx, 
                        target_perc = target_per, is_perc = is_perc, target_length = target_length,join_flag = join_flag, join_hints_truncate = join_hints_truncate, fd_flag = fd_flag)
                        
                        if(prompt[0] == '-1') : 
                                logger.info("Token Limit Exceeded")
                                break_flag = 2
                                break

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
                        target_perc = target_per, is_perc = is_perc, target_length = target_length, aggregate_flag = aggregate_flag, aggregate_hints_truncate = aggregate_hints_truncate, fd_flag = fd_flag)

                        if(prompt[0] == '-1') : 
                                logger.info("Token Limit Exceeded")
                                break_flag = 2
                                break

                        # run llm and get group by column
                        # print(prompt) 
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
                        target_perc = target_per, is_perc = is_perc, target_length = target_length)

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

        print(operation_history)

        if(break_flag == 0) :
                # Generate Table and Compare
                # ss = get_source_with_location(file_count, source_data_name_list,source_data_schema_list, source_samples_list, main_folder, len_idx_target_idx) 
                target_file_location = '{main_folder}/length{len_idx_target_idx}/target_multisource_bayesian_training.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
                ground_truth_location = '{main_folder}/length{len_idx_target_idx}/target.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
                if os.path.isfile(target_file_location):
                        os.remove(target_file_location)
                Path(target_file_location).touch()
                # put this in a loop 
                script_cnt = 0
                error_str = ""
                while(script_cnt < 5) :
                        prompt = get_prompt(prompt_type="python_script", max_tokens = token_limit,model=model,allowed_operation_list=allowed_operation_list,
                                operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema, 
                                target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                                directory = main_folder, len_idx_target_idx = len_idx_target_idx, 
                                target_perc = target_per, is_perc = is_perc, target_length = target_length, error_string = error_str,target_file_location = target_file_location)

                        if(prompt[0] == '-1') : 
                                        logger.info("Token Limit Exceeded")
                                        break_flag = 2
                                        break

                        res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker,type = "Get Python Script")
                        pattern = re.compile(r"```Python(.*?)```", re.DOTALL | re.IGNORECASE)
                        match = pattern.search(res[0])
                        script = match.group(1).strip()
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

logger.info('Total Queries Made : {q}'.format(q = q_count['total']))