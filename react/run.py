from util import (create_connection, execute_sql, print_experiment_settings,
                  log_experiment_success, log_experiment_failed,
                  calculate_similarity, compare_lists_matching)
from parse_json import get_test_info, get_test_cases_ids
from agent import Agent
import os
import csv
import pandas as pd


def main(
        method,
        max_len_id,
        len_id,
        max_target_id,
        target_id,
        max_source_id,
        source_id=0,
        oneshot_source_id=0,
        max_iterations=1,
        json_file_path='./data/chatgpt.json',
        clarify_on=False
):
    conn = create_connection()
    print("Postgres connection established.")
    print(f"target_id: {target_id}, max_target_id: {max_target_id}, "
          f"source_id: {source_id}, max_source_id: {max_source_id}")
    test_cases_list = get_test_cases_ids(json_file_path, len_id, max_len_id, target_id, max_target_id)
    print(f"test_cases_list: {test_cases_list}")
    for test_case in test_cases_list:
        len_id_target_id = test_case[6:]
        # Get the information of the target and source data
        (target_data_name, target_data_schema, target_samples, file_count,
         source_data_name_list, source_data_schema_list, source_samples_list) = (
            get_test_info(json_file_path, len_id_target_id))

        # Create a list to store similarity scores of each iteration
        all_similarity_scores = []

        # Iterative Prompt Optimization and Validation
        iteration_count = 0
        ground_truth_table = []
        validation_table_created = False
        accuracy_list = []
        validation_error_list = []
        sql_errors = ['']
        # Run the experiment
        while True:
            iteration_count += 1
            # check if reached to max number of iterations
            if iteration_count > max_iterations:
                log_experiment_failed(target_data_name, source_data_name_list, iteration_count,
                                      all_similarity_scores, accuracy_list, validation_error_list)
                all_similarity_scores = []
                break

            print(f"*** itr {iteration_count} ***")

            sub_folder_name = f"length{len_id_target_id}"
            # main_folder_name = os.path.abspath("github-pipelines")
            main_folder_name = os.path.abspath("/tmp/github-pipelines")  # Changed to point to /tmp for mac
            target_path = os.path.join(main_folder_name, sub_folder_name, f"target.csv")
            test_0_path = os.path.join(main_folder_name, sub_folder_name, f"test_0.csv")
            result_path = os.path.join(main_folder_name, sub_folder_name, f"Target{len_id_target_id}_result.csv")
            if method == 'baseline':
                result_path = os.path.join(main_folder_name, sub_folder_name,
                                           f"Target{len_id_target_id}_result_baseline.csv")
            source_name = f"Source{len_id_target_id}_{source_id}"
            target_name = f"Target{len_id_target_id}"

            # interact with gpt
            # 　Create agent
            agent = Agent(source_name, target_name, test_0_path, source_data_schema_list, target_data_schema,
                          source_samples_list, target_samples, result_path, clarify_on=clarify_on, method=method)
            agent.prompt = agent.prompt + f"\n\nFix the following Error: {sql_errors[-1]}\n" \
                if (sql_errors[-1] != '') else agent.prompt
            # 　Run agent
            gpt_output = agent.run_baseline() if method == 'baseline' else agent.run()[0]
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


if __name__ == "__main__":
    template_option = 1
    method = 'baseline'
    max_len_id, len_id = 1, 1
    target_id, max_target_id = 0, 99
    source_id, max_source_id = 0, 0
    print_experiment_settings(len_id, max_len_id, target_id, max_target_id, method, clarify_on=False)
    oneshot_source_id = 0  # Set to 0 to disable oneshot
    main(method, max_len_id, len_id, max_target_id, target_id, max_source_id, source_id=0, oneshot_source_id=0,
         max_iterations=5, json_file_path='data/chatgpt.json', clarify_on=False)
