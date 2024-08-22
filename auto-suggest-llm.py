from test_scope import get_test_cases_ids
from llm.llm_models import TokenUsageTracker,LLMClient
from util.utils import get_test_info, execute_python,compare_lists_matching
import time
import auto_suggest_llm_prompts as prt
from auto_suggest_llm_util import create_logger, get_source, get_operation,get_join_hints,get_columns,get_groupby_aggregate_hints,get_source_with_location
import pandas as pd

json_file_path = "data/chatgpt_github_ms.json"
log_dir = "logs-auto-suggest-llm"
len_id = 2
max_len_id = 2
target_id = 11
max_target_id = 30
main_folder = "autopipeline-benchmarks/github-pipelines"

allowed_operation_list = ['JOIN', 'UNION', 'GROUP_BY/AGGREGATE', 'PIVOT', 'UNPIVOT', 'NO_MORE_OPERATION']

task_list = get_test_cases_ids(json_file_path,  len_id, max_len_id, target_id, max_target_id)

logger = create_logger(log_dir,len_id, target_id,max_target_id)

################## Run for each task ##################

for task in task_list :
        logger.info("Started Experiment for "+str(task))

        token_tracker = TokenUsageTracker()

        start_cost_summary = token_tracker.cost_summary()
        print(start_cost_summary)

        len_idx_target_idx = task[6:]

        # print(len_idx_target_idx)

        # Get the information of the target and source data

        (target_data_name, target_data_schema, target_samples, file_count, source_data_name_list,
                source_data_schema_list, source_samples_list) = (
                get_test_info(json_file_path, len_idx_target_idx, main_folder))

        # print(target_data_name, target_data_schema, target_samples, file_count, source_data_name_list,
        #         source_data_schema_list, source_samples_list)

        # 0 to ask for operator and 1 for column and 2 to generate script
        toggle_operator = 0
        history_op = []
        history_elements = []
        operation_history = []

        start_time = time.time()

        llm_client = LLMClient(
                model='gpt-4-turbo', tracker=token_tracker, logger=logger
        )
        source_information = get_source(file_count, source_data_name_list,
                source_data_schema_list, source_samples_list)
        break_flag = 1

        while(break_flag) :

                prompt = prt.get_next_operator_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information)
                res = llm_client.gpt(prompt)
                operation = get_operation(res[0])
                history_op.append(res)

                # operation = 'GROUP_BY'
                print(res)

                match operation :
                        case 'JOIN' :
                                # generate join hints 
                                hints = get_join_hints(file_count,source_data_name_list,source_data_schema_list,main_folder,len_idx_target_idx)
                                # get join prompt 
                                prompt = prt.get_join_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information,hints)
                                res = llm_client.gpt(prompt)
                                print(res)
                                joined_columns = get_columns(res[0])
                                history_elements.append(joined_columns)
                                operation_history.append(operation + ' : ' + str(joined_columns))
                                # run llm and get join columns 
                                # add it to the history
                                pass 
                        case 'GROUP_BY/AGGREGATE' :
                                # generate group by hints 
                                hints = get_groupby_aggregate_hints(file_count,source_data_name_list,source_data_schema_list,main_folder,len_idx_target_idx)
                                # get group by prompt 
                                prompt = prt.get_group_by_aggregate_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information,hints)
                                # run llm and get group by column
                                # print(prompt) 
                                res = llm_client.gpt(prompt)
                                print(res[0])
                                # add it to the history
                                group_by_column = get_columns(res[0])
                                history_elements.append(group_by_column)
                                operation_history.append(operation + ' : [ group_by : {group_by_column[0]}, aggregate : {group_by_column[1]}, aggregation_function : {group_by_column[2]} ]'.format(group_by_column = group_by_column))
                                pass
                        case 'UNION' :
                                prompt = prt.get_union_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information)
                                res = llm_client.gpt(prompt)
                                print(res[0])
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
                if(break_flag == 0) :
                        # generate table
                        # compare table with ground truth
                        pass

        print(operation_history)

        if(break_flag == 0) :
                # Generate Table and Compare
                ss = get_source_with_location(file_count, source_data_name_list,source_data_schema_list, source_samples_list, main_folder, len_idx_target_idx) 
                target_file_location = '{main_folder}/length{len_idx_target_idx}/target_multisource.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
                ground_truth_location = '{main_folder}/length{len_idx_target_idx}/target.csv'.format(main_folder = main_folder, len_idx_target_idx = len_idx_target_idx)
                prompt = prt.get_python_script(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,ss,target_file_location)
                logger.info("Prompt : " + prompt)
                res = llm_client.gpt(prompt)
                script = res[0].split("```Python")[1].split("```")[0].strip()
                # print(script)
                response = execute_python(script)
                print(response)
                if(response == 'Success') : 
                        df_our_response = pd.read_csv(target_file_location)
                        df_ground_truth = pd.read_csv(ground_truth_location)
                        df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)
                        try : 
                                case_accuracy, is_correct, similarity_scores, validation_error = (
                            compare_lists_matching(df_our_response, df_ground_truth))
                                print(case_accuracy,is_correct,similarity_scores,validation_error)
                                logger.info("Task : "+task + " Case Accuracy : "+str(case_accuracy)+ ", is_correct : " + str(is_correct) +", similarity_score : "+ str(similarity_scores) + ", validation_error : " + str(validation_error))
                        except :
                                logger.info("Error : Broken")
                                print("No Match")

                # prompt = prt.get_python_script()
                #  

        end_cost_summary = token_tracker.cost_summary()
        print(end_cost_summary)
        logger.info(end_cost_summary)
        # break

                # break

                # while True :

                #     if(toggle_operator == 0) :
                #         get_prompt_to_ask_for_operator()
                #         operator = get_operator
                #         history_op.append(operator)


                #     if(operator == 'join') :

                #     elif(operator == 'union') : 

                #     elif(operator == 'group_by') : 

                #     elif(operator == 'aggregate') : 









