from test_scope import get_test_cases_ids
from llm.llm_models import TokenUsageTracker,LLMClient
from util.utils import get_test_info, execute_python,compare_lists_matching
import time
import auto_suggest_llm_prompts as prt
from auto_suggest_llm_util import create_logger, get_source, get_operation,get_join_hints,get_columns,get_groupby_aggregate_hints,get_source_with_location, cost_compare, query_gpt, get_columns_aggr,get_columns_join
import pandas as pd

json_file_path = "data/chatgpt_github_ms.json"
log_dir = "logs-auto-suggest-llm"
len_id = 9
max_len_id = 9
target_id = 71
max_target_id = 75
main_folder = "autopipeline-benchmarks/github-pipelines"
model = 'gpt-4-turbo'

allowed_operation_list = ['JOIN', 'UNION', 'GROUP_BY/AGGREGATE', 'PIVOT', 'UNPIVOT', 'NO_MORE_OPERATION']

task_list = get_test_cases_ids(json_file_path,  len_id, max_len_id, target_id, max_target_id)

logger = create_logger(log_dir,len_id, target_id,max_target_id)

q_count = {'total' : 0, 'in_task' : 0}

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
        source_information = get_source(file_count, source_data_name_list,
                source_data_schema_list, source_samples_list)
        break_flag = 1

        while(break_flag) :

                prompt = [prt.get_next_operator_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information)]
                res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Ask For Operator")
                operation = operation = get_operation(res[0])

                match operation :
                        case 'JOIN' :
                                # generate join hints 
                                hints = get_join_hints(file_count,source_data_name_list,source_data_schema_list,main_folder,len_idx_target_idx)
                                # get join prompt 
                                prompt = [prt.get_join_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information,hints)]

                                res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Configure Join")
                                joined_columns = get_columns_join(res[0])
                                history_elements.append(joined_columns)
                                operation_history.append(operation + ' : ' + str(joined_columns))
                                # run llm and get join columns 
                                # add it to the history
                                pass 
                        case 'GROUP_BY/AGGREGATE' :
                                # generate group by hints 
                                hints = get_groupby_aggregate_hints(file_count,source_data_name_list,source_data_schema_list,main_folder,len_idx_target_idx)
                                # get group by prompt 
                                prompt = [prt.get_group_by_aggregate_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information,hints)]
                                # run llm and get group by column
                                # print(prompt) 
                                res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Configure Group by/Aggergate")
                                # print(res[0])
                                # add it to the history
                                group_by_column = get_columns_aggr(res[0])
                                history_elements.append(group_by_column)
                                operation_history.append(operation + ' : [ group_by : {group_by_column[0]}, aggregate : {group_by_column[1]}, aggregation_function : {group_by_column[2]} ]'.format(group_by_column = group_by_column))
                                pass
                        case 'UNION' :
                                prompt = [prt.get_union_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information)]
                                res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Configure Union")
                                # print(res[0])
                                tables_ = get_columns(res[0])
                                history_elements.append(tables_)
                                operation_history.append(operation + ' : ' + str(tables_))
                                pass
                        case 'PIVOT' :
                                operation_history.append(operation)
                                pass 
                        case 'UNPIVOT' :
                                operation_history.append(operation)
                                pass
                        case 'NO_MORE_OPERATION' :
                                # generate python script 
                                # do similarity search 
                                # go to next 
                                break_flag = 0 
                                pass
                        case _ :
                                pass

        print(operation_history)

        if(break_flag == 0) :
                # Generate Table and Compare
                ss = get_source_with_location(file_count, source_data_name_list,source_data_schema_list, source_samples_list, main_folder, len_idx_target_idx) 
                target_file_location = '{main_folder}/length{len_idx_target_idx}/target_multisource.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
                ground_truth_location = '{main_folder}/length{len_idx_target_idx}/target.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
                
                # put this in a loop 
                script_cnt = 0
                error_str = ""
                while(script_cnt < 5) :
                        prompt = [prt.get_python_script(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,ss,target_file_location)]
                        if(script_cnt != 0)  : 
                                prompt[0] = prompt[0] + "\nPrevious execution gave me this error : " + error_str

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

                end_time = time.time()
                if(response == 'Success') : 
                        df_our_response = pd.read_csv(target_file_location,low_memory=False)
                        df_ground_truth = pd.read_csv(ground_truth_location,low_memory=False)
                        df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)
                        try : 
                                case_accuracy, is_correct, similarity_scores, validation_error = (
                            compare_lists_matching(df_our_response, df_ground_truth))
                                print(case_accuracy,is_correct,similarity_scores,validation_error)
                                logger.info("Task : "+task + " Case Accuracy : "+str(case_accuracy)+ ", is_correct : " + str(is_correct) +", similarity_score : "+ str(similarity_scores))
                        except :
                                # logger.info(validation_error)
                                print("Error in calculating accuracy.")

        logger.info('''
        ******Task Summary**********
        Name : {task}
        Total queries made during this task : {q}
        Cost summary : {cost_summary}
        Tasks Used : {oh}
        Time elapsed : {time_elapsed}
        '''.format(task = str(task), q = str(q_count['in_task']), cost_summary = token_tracker.cost_summary(), oh = operation_history, time_elapsed = end_time - start_time))

logger.info('Total Queries Made : {q}'.format(q = q_count['total']))