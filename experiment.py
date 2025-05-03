import ast
import glob
import os
import time

from sklearn.preprocessing import LabelEncoder

from agent import Agent
import csv
import pandas as pd
import logging
from datetime import datetime
from llm.llm_models import TokenUsageTracker
from model.aggregation.pwr import predict_columns
from model.join.pwr import load_trained_model, predict_join_columns
from quality.quality import get_df, data_summary, data_profiling, schema_quality, fd_quality, data_quality, \
    data_morpher, schema_matching
from summary import load_tables, generate_transformation_hints
from util.utils import (create_connection, execute_sql,  execute_python,log_experiment_settings,
                        log_experiment_success, log_experiment_failed,
                        compare_lists_matching, get_test_info, log_experiment, calculate_cost_difference,
                        preprocess_sql_script)
from test_scope import get_test_cases_ids

class Experiment:
    def __init__(self, method, max_pipeline_len_idx, pipeline_len_start_idx, max_target_idx, target_start_idx, backend,
                 log_dir, control_method, script_language, source_start_idx=0,
                 max_attempts=1,main_folder='github-pipelines', data_path='./data/chatgpt.json', clarify_on=False, **kwargs):
        self.task_list = []
        self.logger = None
        self.method = method
        self.max_pipeline_len_idx = max_pipeline_len_idx
        self.pipeline_len_start_idx = pipeline_len_start_idx
        self.max_target_idx = max_target_idx
        self.target_start_idx = target_start_idx
        self.source_start_idx = source_start_idx
        self.backend = backend
        self.max_attempts = max_attempts
        self.main_folder = main_folder
        self.data_path = data_path
        self.token_tracker = TokenUsageTracker()
        self.log_dir = log_dir
        self.clarify_on = clarify_on
        self.control_method = control_method
        self.script_language = script_language

    def create_logger(self):
        # Get current system time
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create the log file name with the current time
        log_file = f"all_similarity_scores_{self.method}_len{self.pipeline_len_start_idx}_target{self.target_start_idx}_source{self.max_target_idx}_{current_time}.log"

        # Check if the log directory exists, create it if it does not
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Setup logging
        logging.basicConfig(filename=os.path.join(self.log_dir, log_file), level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s', filemode='a+')
        return logging.getLogger()

    def setup(self):
        self.task_list = get_test_cases_ids(self.data_path, self.pipeline_len_start_idx,
                                            self.max_pipeline_len_idx, self.target_start_idx, self.max_target_idx)

        print(self.task_list)

        self.logger = self.create_logger()

    def get_llm_friendly_representation(self, source_data_name_list, target_data_name):
        # TODO
        pass

    def _get_agent_args(self, len_idx_target_idx, source_start_idx, method):
        sub_folder_name = f"length{len_idx_target_idx}"
        main_folder_name = os.path.abspath(self.main_folder)
        # main_folder_name = os.path.abspath("/tmp/github-pipelines")  # Changed to point to /tmp for mac
        target_path = os.path.join(main_folder_name, sub_folder_name, f"target.csv")
        test_0_path = os.path.join(main_folder_name, sub_folder_name, f"test_0.csv")
        result_path = os.path.join(main_folder_name, sub_folder_name, f"Target{len_idx_target_idx}_result_{method}.csv")
        # if method == 'monolithic':
        #     result_path = os.path.join(main_folder_name, sub_folder_name,
        #                                f"Target{len_idx_target_idx}_result_baseline.csv")


        source_name = f"Source{len_idx_target_idx}_{source_start_idx}"
        target_name = f"Target{len_idx_target_idx}"
        return source_name, target_name, test_0_path, result_path, target_path

    def run(self):
        log_experiment_settings(self.pipeline_len_start_idx, self.max_pipeline_len_idx,
                                self.target_start_idx, self.max_target_idx, self.method, self.clarify_on)
        conn = create_connection()

        for test_case in self.task_list:

            print(test_case)

            start_cost_summary = self.token_tracker.cost_summary()

            len_idx_target_idx = test_case[6:]


            print(len_idx_target_idx)

            # Get the information of the target and source data

            (target_data_name, target_data_schema, target_samples, file_count, source_data_name_list,
             source_data_schema_list, source_samples_list) = (
                get_test_info(self.data_path, len_idx_target_idx, self.main_folder))

            # Create a list to store similarity scores of each iteration
            all_similarity_scores, accuracy_list = [], []
            validation_error_list = []

            validation_table_created = False
            ground_truth_table = []
            sql_errors = ['']
            fd_feedback = ""
            dq_feedback = ""
            schema_feedback = ""
            hints = ""
            iteration_count = 0
            while True:
                start_time = time.time()
                iteration_count += 1
                # check if reached to max number of iterations
                if iteration_count > self.max_attempts:
                    # log_experiment_failed(target_data_name, source_data_name_list, iteration_count,
                    #                       all_similarity_scores, accuracy_list, validation_error_list)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    end_cost_summary = self.token_tracker.cost_summary()

                    # Calculate the cost of this specific transaction
                    temp_cost = calculate_cost_difference(start_cost_summary, end_cost_summary)
                    log_experiment(target_data_name, source_data_name_list, 0,0, 0,0,execution_time,
                                   temp_cost, 0, self.control_method)
                    all_similarity_scores = []
                    break

                print(f"*** itr {iteration_count} ***")
                cost = self.token_tracker.cost_summary()
                source_name, target_name, test_0_path, result_path, target_path = (
                    self._get_agent_args(len_idx_target_idx, self.source_start_idx, self.method))
                ##test_path should be paths for multiple test cases,finding all path in the father folder of test_0_path
                # Get the directory containing test_0_path
                test_dir = os.path.dirname(test_0_path)

                # Generate the pattern to match all test_*.csv files in the directory
                pattern = os.path.join(test_dir, 'test_*.csv')

                # Use glob to find all matching files
                test_paths = glob.glob(pattern)

                # Optionally, sort the paths if you need them in a specific order
                test_paths.sort()
                agent = Agent(source_data_name_list, target_data_name, target_path,test_paths, source_data_schema_list, target_data_schema,
                              source_samples_list, target_samples, result_path, self.control_method,self.token_tracker, self.logger,
                              backend=self.backend, script_language=self.script_language,
                              clarify_on=self.clarify_on, method=self.method)
                whether_multi = True if self.method == 'multi_source' else False
                ##Monolithic prompt only
                if self.control_method == 'none':
                    # Run the experiment
                    agent.prompt = agent.prompt + f"\n\nFix the following Error: {sql_errors[-1]}\n" \
                        if (sql_errors[-1] != '') else agent.prompt
                    print(f"Prompt: {agent.prompt}")
                    end_time_1 = time.time()
                    execution_time_1 = end_time_1 - start_time
                    gpt_output = agent.run(method=self.method)
                    end_cost_summary = self.token_tracker.cost_summary()

                    # Calculate the cost of this specific transaction
                    temp_cost = calculate_cost_difference(start_cost_summary, end_cost_summary)
                    self.logger.info(f"SQL/Python Script Extracted from GPT Response:\n {gpt_output}")
                    print("SQL/Python Script Extracted from GPT Response:")
                    print(gpt_output)

                    # execute some table creation and data importing

                    end_time_2 = time.time()
                    execution_time_2 = end_time_2 - end_time_1
                    # Execute the SQL script on the specified table
                    execution_result = execute_sql(conn, gpt_output) if self.script_language == 'sql' else execute_python(gpt_output)
                    end_time = time.time()
                    execution_time_3 = end_time - end_time_2
                    # print(f"Execution Result: {execution_result}")
                    if "Error:" in execution_result:
                        self.logger.error(f"iter{iteration_count} Error in the previous response {execution_result}")
                        print(f"\n iter{iteration_count} Error in the previous response: {execution_result}")
                        with open('log/all_similarity_scores.log', 'a+') as file:
                            file.write(f"{target_data_name} <- {source_data_name_list}")
                            file.write(f"\t\t\t\t[Failed]\n\tError in the previous response: {execution_result}\n")
                        accuracy_list.append(0.0)
                        # break
                        sql_errors.append(execution_result)
                        continue

                    # not using execution_result directly, as numeric vs string values will occur while validation
                    our_result = []
                    try:
                        with open(result_path, 'r', encoding="utf-8") as file:
                            reader = csv.reader(file)
                            header = next(reader)
                            for row in reader:
                                our_result.append(tuple(row))
                        execution_result_df = pd.DataFrame(our_result,columns=header)
                    except Exception as e:
                        self.logger.error(f"Error while reading the result file: {e}")
                        print(f"Error while reading the result file: {e}")
                        continue
                    # SQL script returned by ChatGPT is executed correctly
                    if (validation_table_created == False):
                        with open(target_path, 'r', encoding="utf-8") as file:
                            reader = csv.reader(file)
                            header = next(reader)
                            for row in reader:
                                ground_truth_table.append(tuple(row))
                        validation_table_created = True
                    ground_truth_table_df = pd.DataFrame(ground_truth_table,columns=header)
                    # Validate the ChatGPT generated SQL script
                    # quality score if score > threshold else continue
                    try:
                        case_accuracy, is_correct, similarity_scores, validation_error = (
                            compare_lists_matching(execution_result_df, ground_truth_table_df))

                        print(case_accuracy)
                        print(is_correct)
                        print(similarity_scores)
                        print(validation_error)
                    except Exception as e:
                        self.logger.error(f"Error while comparing the results: {e}")
                        print(f"Error while comparing the results: {e}")
                        end_time = time.time()
                        execution_time = end_time - start_time
                        log_experiment(target_data_name, source_data_name_list,0, execution_time_1,execution_time_2, execution_time_3,0,
                                       temp_cost, 0, self.control_method)
                        break

                    accuracy_list.append(case_accuracy)
                    validation_error_list.append(validation_error)
                    all_similarity_scores.append(similarity_scores)
                    print(is_correct)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    if is_correct:
                        log_experiment_success(target_data_name, source_data_name_list, iteration_count)
                        print("Execution time: ", execution_time)
                        log_experiment(target_data_name, source_data_name_list, case_accuracy,execution_time_1,execution_time_2, execution_time_3,execution_time,
                                       temp_cost, 1, self.control_method)
                        break
                    else:
                        # if not is_correct:
                        self.logger.error(f"The returned SQL/Python script can run, but the execution result of the SQL is wrong: "
                              f"{validation_error}. Please try again.")
                        print(f"The returned SQL/Python script can run, but the execution result of the SQL is wrong: "
                              f"{validation_error}. Please try again.")
                        log_experiment(target_data_name, source_data_name_list, case_accuracy,execution_time_1,execution_time_2, execution_time_3,execution_time,
                                       temp_cost, 0, self.control_method)
                        break
                ##Monolithic prompt with data summary
                if self.control_method == 'summary':
                    source_dfs, target_df = get_df(**agent.agent_attrs)
                    # # Data profiling for the target table
                    # target_sa, target_ma, target_d = data_profiling(target_df)
                    # print("single analysis for target:",target_sa)
                    # hints_target = data_summary(target_sa, target_ma, target_d)
                    #
                    # # Initialize a string to hold all source summaries
                    # all_source_summaries = ""
                    # if self.method == 'multi_source':
                    #     # Loop through each source dataframe, profile it and get the summary
                    #     for i, source_df in enumerate(source_dfs):
                    #         source_sa, source_ma = data_profiling(source_df, True)
                    #         hints_source = data_summary(source_sa, source_ma, 0, True)
                    #         print("single analysis for source:", source_sa)
                    #         # Append each source summary to the string
                    #         all_source_summaries += f"\nHere is data summary for source table {i}:\n{hints_source}" if hints_source else ""
                    # else:
                    #     source_sa, source_ma = data_profiling(source_dfs, True)
                    #     hints_source = data_summary(source_sa, source_ma, 0, True)
                    #
                    #     # Append each source summary to the string
                    #     all_source_summaries += f"\nHere is data summary for source table: \n{hints_source}" if hints_source else ""
                    #
                    # # Add the summaries to the agent's prompt
                    # agent.prompt += all_source_summaries
                    # agent.prompt += f"\nHere is data summary for target table:\n{hints_target}" if hints_target else ""
                    # if whether_multi:
                    #     hints_join = schema_matching(source_dfs,target_df)
                    #     for hint in hints_join:
                    #         agent.prompt += "\n"+hint
                    # # Run the experiment
                    # agent.prompt = agent.prompt + f"\n\nFix the following Error: {sql_errors[-1]}\n" \
                    #     if (sql_errors[-1] != '') else agent.prompt

                    #summary
                    tables = load_tables(test_dir)
                    # Load the models
                    join_model = load_trained_model('model/join/join_model.json')
                    key_model = load_trained_model('model/aggregation/key_model.json')
                    # Predict join column pairs
                    join_candidates = predict_join_columns(tables, join_model)
                    candidate_matching_columns = [(f"{t1}.{c1}", f"{t2}.{c2}", s) for (t1, c1), (t2, c2), s in
                                                  join_candidates]
                    # Predict key columns for the target table
                    target_table_name = 'target'
                    target_df = tables[target_table_name]
                    # Fit LabelEncoder on all possible data types
                    all_data_types = ['int64', 'float64', 'object']  # Add more types if needed
                    label_encoder = LabelEncoder()
                    label_encoder.fit(all_data_types)
                    # Predict key columns for all tables
                    all_key_candidates = []
                    key_candidates = predict_columns(tables, key_model, label_encoder)
                    for table_name, table_df in tables.items():
                        all_key_candidates.extend([(table_name, col, score) for tab, col, score in key_candidates])

                    # Generate transformation hints
                    source_dfs = [tables[table] for table in tables if table != target_table_name]
                    hints = generate_transformation_hints(tables,source_dfs, target_df, mode='dynamic',
                                                          candidate_matching_columns=candidate_matching_columns,
                                                          candidate_key_columns=all_key_candidates)

                    hints_str = '\n'.join(hints)
                    agent.prompt += hints_str
                    print(f"Prompt: {agent.prompt}")
                    end_time_1 = time.time()
                    execution_time_1 = end_time_1 - start_time
                    gpt_output = agent.run(method=self.method)
                    gpt_output = preprocess_sql_script(gpt_output)
                    print("Preprocessed GPT Response:", gpt_output)
                    end_cost_summary = self.token_tracker.cost_summary()

                    # Calculate the cost of this specific transaction
                    temp_cost = calculate_cost_difference(start_cost_summary, end_cost_summary)
                    self.logger.info(f"SQL Script Extracted from GPT Response:\n {gpt_output}")
                    print("SQL Script Extracted from GPT Response:")
                    print(gpt_output)
                    end_time_2 = time.time()
                    execution_time_2 = end_time_2 - end_time_1
                    # Execute the SQL script on the specified table
                    execution_result = execute_sql(conn, gpt_output) if self.script_language == 'sql' else execute_python(gpt_output)
                    end_time = time.time()
                    execution_time_3 = end_time - end_time_2
                    # print(f"SQL Result: {execution_result}")
                    if "Error:" in execution_result:
                        self.logger.error(f"iter{iteration_count} Error in the previous response {execution_result}")
                        print(f"\n iter{iteration_count} Error in the previous response: {execution_result}")
                        with open('log/all_similarity_scores.log', 'a+') as file:
                            file.write(f"{target_data_name} <- {source_data_name_list}")
                            file.write(f"\t\t\t\t[Failed]\n\tError in the previous response: {execution_result}\n")
                        accuracy_list.append(0.0)
                        # break
                        sql_errors.append(execution_result)
                        end_time = time.time()
                        execution_time = end_time - start_time
                        log_experiment(target_data_name, source_data_name_list,0, execution_time_1, execution_time_2,
                                       execution_time_3, 0,
                                       temp_cost, 0, self.control_method)
                        break
                    # not using sql_result directly, as numeric vs string values will occur while validation
                    our_result = []
                    try:
                        with open(result_path, 'r', encoding="utf-8") as file:
                            reader = csv.reader(file)
                            header = next(reader)
                            for row in reader:
                                our_result.append(tuple(row))
                        execution_result_df = pd.DataFrame(our_result,columns=header)
                    except Exception as e:
                        self.logger.error(f"Error while reading the result file: {e}")
                        print(f"Error while reading the result file: {e}")
                        end_time = time.time()
                        execution_time = end_time - start_time
                        log_experiment(target_data_name, source_data_name_list,0, execution_time_1, execution_time_2,
                                       execution_time_3, 0,
                                       temp_cost, 0, self.control_method)
                        break

                    # SQL script returned by ChatGPT is executed correctly
                    if (validation_table_created == False):
                        with open(target_path, 'r', encoding="utf-8") as file:
                            reader = csv.reader(file)
                            header = next(reader)
                            for row in reader:
                                ground_truth_table.append(tuple(row))
                        validation_table_created = True
                    ground_truth_table_df = pd.DataFrame(ground_truth_table,columns=header)
                    # Validate the ChatGPT generated SQL script
                    # quality score if score > threshold else continue

                    try:
                        case_accuracy, is_correct, similarity_scores, validation_error = (
                            compare_lists_matching(execution_result_df, ground_truth_table_df))
                    except Exception as e:
                        self.logger.error(f"Error while comparing the results: {e}")
                        print(f"Error while comparing the results: {e}")
                        end_time = time.time()
                        execution_time = end_time - start_time
                        log_experiment(target_data_name, source_data_name_list,0, execution_time_1, execution_time_2,
                                       execution_time_3, 0,
                                       temp_cost, 0, self.control_method)
                        break
                    end_time = time.time()
                    execution_time = end_time - start_time
                    if is_correct:
                        log_experiment_success(target_data_name, source_data_name_list, iteration_count)
                        print("Execution time: ", execution_time)
                        log_experiment(target_data_name, source_data_name_list,case_accuracy, execution_time_1,execution_time_2, execution_time_3,execution_time,
                                       temp_cost, 1, self.control_method)
                        break
                    else:
                        # if not is_correct:
                        self.logger.error(
                            f"The returned SQL script can run, but the execution result of the SQL is wrong: "
                            f"{validation_error}. Please try again.")
                        print(f"The returned SQL script can run, but the execution result of the SQL is wrong: "
                              f"{validation_error}. Please try again.")
                        log_experiment(target_data_name, source_data_name_list,case_accuracy, execution_time_1,execution_time_2, execution_time_3,execution_time,
                                       temp_cost, 0, self.control_method)
                        break
                ##Monolithic prompt with data quality
                if self.control_method == 'quality':

                    source_dfs, target_df = get_df(**agent.agent_attrs)
                    agent.prompt = agent.prompt + schema_feedback + dq_feedback + fd_feedback
                    # Run the experiment
                    agent.prompt = agent.prompt + f"\n\nFix the following Error: {sql_errors[-1]}\n" \
                        if (sql_errors[-1] != '') else agent.prompt
                    print(f"Prompt: {agent.prompt}")
                    end_time_1 = time.time()
                    execution_time_1 = end_time_1 - start_time
                    gpt_output = agent.run(method=self.method)
                    gpt_output = preprocess_sql_script(gpt_output)
                    print("Preprocessed GPT Response:", gpt_output)
                    end_cost_summary = self.token_tracker.cost_summary()
                    # Calculate the cost of this specific transaction
                    temp_cost = calculate_cost_difference(start_cost_summary, end_cost_summary)
                    self.logger.info(f"SQL Script Extracted from GPT Response:\n {gpt_output}")
                    print("SQL Script Extracted from GPT Response:")
                    print(gpt_output)
                    end_time_2 = time.time()
                    execution_time_2 = end_time_2 - end_time_1
                    # if whether_multi:
                    #     schema_score, schema_feedback = 0, ''
                    # else:
                    #     schema_score, schema_feedback, column_mappings, target_handle = schema_quality(gpt_output,
                    #                                                                                **agent.agent_attrs)
                    # Execute the SQL script on the specified table
                    execution_result = execute_sql(conn, gpt_output) if self.script_language == 'sql' else execute_python(gpt_output)
                    end_time = time.time()
                    execution_time_3 = end_time - end_time_2
                    # print(f"SQL Result: {execution_result}")
                    if not execution_result:
                        print("The SQL result is empty. Skipping to the next iteration.")
                        # Skip the rest of the code in this iteration and continue with the next one
                        continue  # Assuming this code is within a loop
                    if "Error:" in execution_result:
                        self.logger.error(f"iter{iteration_count} Error in the previous response {execution_result}")
                        print(f"\n iter{iteration_count} Error in the previous response: {execution_result}")
                        with open('log/all_similarity_scores.log', 'a+') as file:
                            file.write(f"{target_data_name} <- {source_data_name_list}")
                            file.write(f"\t\t\t\t[Failed]\n\tError in the previous response: {execution_result}\n")
                        accuracy_list.append(0.0)
                        # break
                        sql_errors.append(execution_result)
                        continue

                    # not using execution_result directly, as numeric vs string values will occur while validation
                    our_result = []
                    try:
                        with open(result_path, 'r', encoding="utf-8") as file:
                            reader = csv.reader(file)
                            header = next(reader)
                            for row in reader:
                                our_result.append(tuple(row))
                        execution_result_df = pd.DataFrame(our_result,columns=header)
                    except Exception as e:
                        self.logger.error(f"Error while reading the result file: {e}")
                        print(f"Error while reading the result file: {e}")
                        continue

                    target_handle = ast.literal_eval(target_data_schema)
                    # Data Quality
                    dq_score, low_quality_columns = data_quality(our_result, target_handle,whether_multi)
                    if low_quality_columns is not None and not whether_multi:
                        dq_feedback = f"Some hints for the schema changes from the first table to the second table:Consider using aggregation functions and group by {low_quality_columns}." if low_quality_columns else ""
                    elif low_quality_columns is not None and whether_multi:
                        if self.script_language == 'sql':
                            dq_feedback = f"Please use 'WHERE' command to make sure column {low_quality_columns} is not NULL in the target table."
                        else:
                            dq_feedback = f"Please use inner join to make sure column {low_quality_columns} is not NULL in the target table."


                    if whether_multi:
                        fd_score, fd_feedback = 0, ''
                    else:
                        fd_score, fd_feedback = fd_quality(gpt_output, column_mappings,low_quality_columns, **agent.agent_attrs)

                    final_score = (schema_score + dq_score + fd_score) / 3
                    # SQL script returned by ChatGPT is executed correctly
                    if (validation_table_created == False):
                        with open(target_path, 'r', encoding="utf-8") as file:
                            reader = csv.reader(file)
                            header = next(reader)
                            for row in reader:
                                ground_truth_table.append(tuple(row))
                        validation_table_created = True
                    ground_truth_table_df = pd.DataFrame(ground_truth_table,columns=header)
                    # Validate the ChatGPT generated SQL script
                    # quality score if score > threshold else continue

                    try:
                        case_accuracy, is_correct, similarity_scores, validation_error = (
                            compare_lists_matching(execution_result_df, ground_truth_table_df))
                    except Exception as e:
                        self.logger.error(f"Error while comparing the results: {e}")
                        print(f"Error while comparing the results: {e}")
                        end_time = time.time()
                        execution_time = end_time - start_time
                        log_experiment(target_data_name, source_data_name_list, 0,execution_time_1, execution_time_2,
                                       execution_time_3, 0,
                                       temp_cost, 0, self.control_method)
                        break

                    if is_correct:
                        log_experiment_success(target_data_name, source_data_name_list, iteration_count)
                        end_time = time.time()
                        execution_time = end_time - start_time
                        print("Execution time: ", execution_time)
                        log_experiment(target_data_name, source_data_name_list,case_accuracy, execution_time_1,execution_time_2, execution_time_3,execution_time,
                                       temp_cost, 1, self.control_method)
                        break
                    else:
                        # if not is_correct:
                        self.logger.error(
                            f"The returned SQL script can run, but the execution result of the SQL is wrong: "
                            f"{validation_error}. Please try again.")
                        print(f"The returned SQL script can run, but the execution result of the SQL is wrong: "
                              f"{validation_error}. Please try again.")
                        if iteration_count >= self.max_attempts:
                            end_time = time.time()
                            execution_time = end_time - start_time
                            print("Execution time: ", execution_time)
                            log_experiment(target_data_name, source_data_name_list,case_accuracy, execution_time_1,execution_time_2, execution_time_3,execution_time,
                                       temp_cost, 0, self.control_method)
                            break
                        else:
                            if schema_feedback or dq_feedback or fd_feedback:
                                continue
                            else:
                                end_time = time.time()
                                execution_time_3 = end_time - end_time_2
                                execution_time = end_time - start_time
                                print("Execution time: ", execution_time)
                                log_experiment(target_data_name, source_data_name_list,case_accuracy, execution_time_1,execution_time_2, execution_time_3,execution_time,
                                               temp_cost, 0, self.control_method)
                                break
                ##Monolithic prompt with data quality and data summary
                if self.control_method == 'both':
                    source_dfs, target_df = get_df(**agent.agent_attrs)
                    # Data profiling for the target table
                    target_sa, target_ma, target_d = data_profiling(target_df)
                    hints_target = data_summary(target_sa, target_ma, target_d)

                    # Initialize a string to hold all source summaries
                    all_source_summaries = ""

                    if self.method == 'multi_source':
                        # Loop through each source dataframe, profile it and get the summary
                        for i, source_df in enumerate(source_dfs):
                            source_sa, source_ma = data_profiling(source_df, True)
                            hints_source = data_summary(source_sa, source_ma, 0, True)

                            # Append each source summary to the string
                            all_source_summaries += f"\nHere is data summary for source table {i}:\n{hints_source}" if hints_source else ""
                    else:
                        source_sa, source_ma = data_profiling(source_dfs, True)
                        hints_source = data_summary(source_sa, source_ma, 0, True)

                        # Append each source summary to the string
                        all_source_summaries += f"\nHere is data summary for source table: \n{hints_source}" if hints_source else ""

                    # Add the summaries to the agent's prompt
                    agent.prompt += all_source_summaries
                    agent.prompt += f"\nHere is data summary for target table:\n{hints_target}" if hints_target else ""
                    if whether_multi:
                        hints_join = schema_matching(source_dfs)
                        for hint in hints_join:
                            agent.prompt += "\n"+hint
                    agent.prompt = agent.prompt + schema_feedback + hints
                    # Run the experiment
                    agent.prompt = agent.prompt + f"\n\nFix the following Error: {sql_errors[-1]}\n" \
                        if (sql_errors[-1] != '') else agent.prompt
                    print(f"Prompt: {agent.prompt}")
                    end_time_1 = time.time()
                    execution_time_1 = end_time_1 - start_time

                    gpt_output = agent.run(method=self.method)
                    gpt_output = preprocess_sql_script(gpt_output)
                    #print("Preprocessed GPT Response:", gpt_output)
                    end_cost_summary = self.token_tracker.cost_summary()
                    # Calculate the cost of this specific transaction
                    temp_cost = calculate_cost_difference(start_cost_summary, end_cost_summary)
                    end_time_2 = time.time()
                    execution_time_2 = end_time_2 - end_time_1
                    self.logger.info(f"SQL Script Extracted from GPT Response:\n {gpt_output}")
                    #print("SQL Script Extracted from GPT Response:")
                    print(gpt_output)
                    if whether_multi:
                        schema_score, schema_feedback = 0, ''
                    else:
                        schema_score, schema_feedback, column_mappings, target_handle = schema_quality(gpt_output,
                                                                                                   **agent.agent_attrs)
                    # Execute the SQL script on the specified table
                    execution_result = execute_sql(conn, gpt_output) if self.script_language == 'sql' else execute_python(gpt_output)
                    end_time_3 = time.time()
                    execution_time_3 = end_time_3 - end_time_2
                    if not execution_result:
                        print("The SQL result is empty. Skipping to the next iteration.")
                        # Skip the rest of the code in this iteration and continue with the next one
                        continue  # Assuming this code is within a loop
                    # print(f"SQL Result: {execution_result}")
                    if "Error:" in execution_result:
                        self.logger.error(f"iter{iteration_count} Error in the previous response {execution_result}")
                        print(f"\n iter{iteration_count} Error in the previous response: {execution_result}")
                        with open('log/all_similarity_scores.log', 'a+') as file:
                            file.write(f"{target_data_name} <- {source_data_name_list}")
                            file.write(f"\t\t\t\t[Failed]\n\tError in the previous response: {execution_result}\n")
                        accuracy_list.append(0.0)
                        # break
                        sql_errors.append(execution_result)
                        continue

                    # not using execution_result directly, as numeric vs string values will occur while validation
                    our_result = []
                    try:
                        with open(result_path, 'r', encoding="utf-8") as file:
                            reader = csv.reader(file)
                            header = next(reader)
                            for row in reader:
                                our_result.append(tuple(row))
                        execution_result_df = pd.DataFrame(our_result,columns=header)
                    except Exception as e:
                        self.logger.error(f"Error while reading the result file: {e}")
                        print(f"Error while reading the result file: {e}")
                        continue
                    result_sa, result_ma, result_d = data_profiling(execution_result_df)

                    hints = data_morpher(target_sa, target_ma, target_d, result_sa, result_ma, result_d,whether_multi)

                    # SQL script returned by ChatGPT is executed correctly
                    if (validation_table_created == False):
                        with open(target_path, 'r', encoding="utf-8") as file:
                            reader = csv.reader(file)
                            header = next(reader)
                            for row in reader:
                                ground_truth_table.append(tuple(row))
                        validation_table_created = True
                    ground_truth_table_df = pd.DataFrame(ground_truth_table,columns=header)
                    # Validate the ChatGPT generated SQL script
                    # quality score if score > threshold else continue

                    try:
                        case_accuracy, is_correct, similarity_scores, validation_error = (
                            compare_lists_matching(execution_result_df, ground_truth_table_df))
                    except Exception as e:
                        self.logger.error(f"Error while comparing the results: {e}")
                        print(f"Error while comparing the results: {e}")
                        end_time = time.time()
                        execution_time = end_time - start_time
                        log_experiment(target_data_name, source_data_name_list,0, execution_time_1, execution_time_2,
                                       execution_time_3, 0,
                                       temp_cost, 0, self.control_method)
                        break

                    if is_correct:
                        end_time = time.time()
                        execution_time = end_time - start_time
                        log_experiment_success(target_data_name, source_data_name_list, iteration_count)
                        log_experiment(target_data_name, source_data_name_list,case_accuracy, execution_time_1,execution_time_2, execution_time_3,execution_time,
                                       temp_cost, 1, self.control_method)
                        break
                    else:
                        if hints:
                            self.logger.error(
                            f"The returned SQL script can run, but the execution result of the SQL is wrong: "
                            f"{validation_error}. Please try again.")
                            print(f"The returned SQL script can run, but the execution result of the SQL is wrong: "
                              f"{validation_error}. Please try again.")
                            continue
                        else:
                            end_time = time.time()
                            execution_time = end_time - start_time
                            print("Execution time: ", execution_time)
                            log_experiment(target_data_name, source_data_name_list,case_accuracy, execution_time_1,execution_time_2, execution_time_3,execution_time,
                                           temp_cost, 0, self.control_method)
                            break
                        # if not is_correct:

        print("All similarity scores saved to all_similarity_scores.log.")
        conn.close()

    def __repr__(self):
        return f"Experiment(method={self.method}, max_pipeline_len_idx={self.max_pipeline_len_idx}, pipeline_len_start_idx={self.pipeline_len_start_idx}, " \
               f"max_target_idx={self.max_target_idx}, target_start_idx={self.target_start_idx}, " \
               f"source_start_idx={self.source_start_idx}, " \
               f"max_attempts={self.max_attempts}, data_path={self.data_path}, " \
               f"clarify_on={self.clarify_on})"

    def __str__(self):
        return f"Experiment(method={self.method}, max_pipeline_len_idx={self.max_pipeline_len_idx}, pipeline_len_start_idx={self.pipeline_len_start_idx}, " \
               f"max_target_idx={self.max_target_idx}, target_start_idx={self.target_start_idx}, " \
               f"source_start_idx={self.source_start_idx},  " \
               f"max_attempts={self.max_attempts}, data_path={self.data_path}, " \
               f"clarify_on={self.clarify_on})"

    def to_dict(self):
        return {
            'method': self.method,
            'max_pipeline_len_idx': self.max_pipeline_len_idx,
            'pipeline_len_start_idx': self.pipeline_len_start_idx,
            'max_target_idx': self.max_target_idx,
            'target_start_idx': self.target_start_idx,
            'max_source_idx': self.max_source_idx,
            'source_start_idx': self.source_start_idx,
            'max_attempts': self.max_attempts,
            'data_path': self.data_path,
            'clarify_on': self.clarify_on
        }

    def visualize_experiment_results(self):
        # TODO
        pass
