import os
from agent import Agent
import csv
import pandas as pd
import logging
from datetime import datetime
from llm.llm_models import TokenUsageTracker
from util.utils import (create_connection, execute_sql, log_experiment_success, log_experiment_failed,
                        compare_lists_matching, get_test_info, get_test_cases_ids)


class Experiment:
    def __init__(self, method, max_pipeline_len_idx, pipeline_len_start_idx, max_target_idx, target_start_idx, backend,
                 log_dir, source_start_idx=0,
                 max_attempts=1, data_path='./data/chatgpt.json', clarify_on=False, **kwargs):
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
        self.data_path = data_path
        self.token_tracker = TokenUsageTracker()
        self.log_dir = log_dir
        self.clarify_on = clarify_on

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
        self.logger = self.create_logger()

    def get_llm_friendly_representation(self, source_data_name_list, target_data_name):
        # TODO
        pass

    def _get_agent_args(self, len_idx_target_idx, source_start_idx, method):
        sub_folder_name = f"length{len_idx_target_idx}"
        main_folder_name = os.path.abspath("github-pipelines")
        # main_folder_name = os.path.abspath("/tmp/github-pipelines")  # Changed to point to /tmp for mac
        target_path = os.path.join(main_folder_name, sub_folder_name, f"target.csv")
        test_0_path = os.path.join(main_folder_name, sub_folder_name, f"test_0.csv")
        result_path = os.path.join(main_folder_name, sub_folder_name, f"Target{len_idx_target_idx}_result.csv")
        if method == 'monolithic':
            result_path = os.path.join(main_folder_name, sub_folder_name,
                                       f"Target{len_idx_target_idx}_result_baseline.csv")
        source_name = f"Source{len_idx_target_idx}_{source_start_idx}"
        target_name = f"Target{len_idx_target_idx}"
        return source_name, target_name, test_0_path, result_path, target_path

    def run(self):
        conn = create_connection()

        for test_case in self.task_list:
            len_idx_target_idx = test_case[6:]
            # Get the information of the target and source data

            (target_data_name, target_data_schema, target_samples, file_count, source_data_name_list,
             source_data_schema_list, source_samples_list) = (
                get_test_info(self.data_path, len_idx_target_idx))

            # Create a list to store similarity scores of each iteration
            all_similarity_scores, accuracy_list = [], []
            validation_error_list = []

            validation_table_created = False
            ground_truth_table = []
            sql_errors = ['']
            xx_feedback = ['']
            iteration_count = 0
            while True:
                iteration_count += 1
                # check if reached to max number of iterations
                if iteration_count > self.max_attempts:
                    log_experiment_failed(target_data_name, source_data_name_list, iteration_count,
                                          all_similarity_scores, accuracy_list, validation_error_list)
                    all_similarity_scores = []
                    break

                print(f"*** itr {iteration_count} ***")

                source_name, target_name, test_0_path, result_path, target_path = (
                    self._get_agent_args(len_idx_target_idx, self.source_start_idx, self.method))

                agent = Agent(source_name, target_name, test_0_path, source_data_schema_list, target_data_schema,
                              source_samples_list, target_samples, result_path, self.token_tracker, self.logger,
                              backend=self.backend,
                              clarify_on=self.clarify_on, method=self.method)

                # Run the experiment
                agent.prompt = agent.prompt + f"\n\nFix the following Error: {sql_errors[-1]}\n" \
                    if (sql_errors[-1] != '') else agent.prompt

                gpt_output = agent.run_baseline() if self.method == 'monolithic' else agent.run()[0]
                print("SQL Script Extracted from GPT Response:")
                print(gpt_output)

                # Execute the SQL script on the specified table
                sql_result = execute_sql(conn, gpt_output)
                # print(f"SQL Result: {sql_result}")
                if "Error:" in sql_result:
                    print(f"\n iter{iteration_count} Error in the previous response: {sql_result}")
                    with open('log/all_similarity_scores.log', 'a+') as file:
                        file.write(f"{target_data_name} <- {source_data_name_list}")
                        file.write(f"\t\t\t\t[Failed]\n\tError in the previous response: {sql_result}\n")
                    accuracy_list.append(0.0)
                    # break
                    sql_errors.append(sql_result)
                    continue
                # not using sql_result directly, as numeric vs string values will occur while validation
                our_result = []
                with open(result_path, 'r', encoding="utf-8") as file:
                    reader = csv.reader(file)
                    header = next(reader)
                    for row in reader:
                        our_result.append(tuple(row))
                sql_result_df = pd.DataFrame(our_result)

                # SQL script returned by ChatGPT is executed correctly
                if (validation_table_created == False):
                    with open(target_path, 'r', encoding="utf-8") as file:
                        reader = csv.reader(file)
                        header = next(reader)
                        for row in reader:
                            ground_truth_table.append(tuple(row))
                    validation_table_created = True
                ground_truth_table_df = pd.DataFrame(ground_truth_table)
                # Validate the ChatGPT generated SQL script
                # quality score if score > threshold else continue

                case_accuracy, is_correct, similarity_scores, validation_error = (
                    compare_lists_matching(sql_result_df, ground_truth_table_df))

                accuracy_list.append(case_accuracy)
                validation_error_list.append(validation_error)
                all_similarity_scores.append(similarity_scores)
                print(is_correct)

                if is_correct:
                    log_experiment_success(target_data_name, source_data_name_list, iteration_count)
                    all_similarity_scores = []
                    break
                else:
                    print(f"The returned SQL script can run, but the execution result of the SQL is wrong: "
                          f"{validation_error}. Please try again.")
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
