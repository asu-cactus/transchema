from test_scope import get_test_cases_ids
from llm.llm_models import TokenUsageTracker,LLMClient
from util.utils import get_test_info, execute_python, compare_lists_matching
import time
import auto_suggest_llm_prompts as prt
from auto_suggest_llm_util import create_logger, get_source, get_operation, get_columns, query_gpt,  get_columns_join, get_prompt, cost_compare
import pandas as pd
import re
import sys
from pathlib import Path
import parameters as p


# decided through parameters
len_id = p.len_id
max_len_id = p.max_len_id
target_id = p.target_id #[11,18,22,25,62,10,16,31,38,5] # [18,2,32,33,96,16,27,78,91,18]
max_target_id = p.max_target_id
target_per = p.target_per
is_perc = p.is_perc
hint_source = p.hint_source # v1_kv, v1_text or v2(Xuanmao's hints)
anon_flag = p.anon_flag

#2
# target_length = int(max(3,10*0.9695545786258186))
# source_length = int(max(3,10*0.09828012752411708))

#3
target_length = p.target_length
source_length = p.source_length

join_flag = p.join_flag
aggregate_flag = p.aggregate_flag

#2
# join_hints_truncate = [0.9006759015810097,0.11102115895485554,0.5241539295936876,0.021526354616419163,0.9722678489028443,0.5997167278729312]
# aggregate_hints_truncate = [0.9006759015810097,0.5797659415180153,0.46440152668695256,0.8109176073751933]

#3
#join_hints = [dvr, js, jc, vro, leftness, sortedness]
# aggregate_hints = [dvr_ub,dvr_lb, leftness_ub,leftness_lb, emptiness_ub,emptiness_lb, peak_frequency_ub, peak_frequency_lb,value_range_ub, value_range_lb]
join_hints_truncate = p.join_hints_truncate
aggregate_hints_truncate = p.aggregate_hints_truncate


fd_flag = p.fd_flag
token_limit = p.token_limit
model = p.model


json_file_path = "data/chatgpt_github_ms.json"
log_dir = p.log_dir
main_folder = "autopipeline-benchmarks/github-pipelines"

allowed_operation_list = ['JOIN', 'UNION', 'GROUP_BY/AGGREGATE', 'PIVOT', 'UNPIVOT', 'NO_MORE_OPERATION']

task_list = get_test_cases_ids(json_file_path,  len_id, max_len_id, target_id, max_target_id)

logger = create_logger("",log_dir,len_id, target_id,max_target_id)

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
                get_test_info(json_file_path, len_idx_target_idx, main_folder,anon_flag))


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

        # print(operation_history)

        if(break_flag == 0) :
                # Generate Table and Compare
                # ss = get_source_with_location(file_count, source_data_name_list,source_data_schema_list, source_samples_list, main_folder, len_idx_target_idx) 
                target_file_location = '{main_folder}/length{len_idx_target_idx}/target_multisource.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
                ground_truth_location = '{main_folder}/length{len_idx_target_idx}/target.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
                Path(target_file_location).touch()
                # put this in a loop 
                script_cnt = 0
                error_str = ""
                while(script_cnt < 5) :
                        prompt = get_prompt(prompt_type="python_script", max_tokens = token_limit,model=model,allowed_operation_list=allowed_operation_list,
                                operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema, 
                                target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                                directory = main_folder, len_idx_target_idx = len_idx_target_idx, 
                                target_perc = target_per, is_perc = is_perc, target_length = target_length, error_string = error_str,target_file_location = target_file_location, hint_source = hint_source)

                        if(prompt[0] == '-1') : 
                                        logger.info("Token Limit Exceeded")
                                        break_flag = 2
                                        break

                        res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker,type = "Get Python Script")
                        script = res[0].split("```Python")[1].split("```")[0].strip()
                        # print(script)
                        response = execute_python(script)
                        # print(response)
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