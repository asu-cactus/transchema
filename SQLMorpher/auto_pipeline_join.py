import os
import pandas as pd
import json
from datetime import datetime
from util import (create_connection, execute_sql, print_experiment_settings,
                   log_experiment_success, log_experiment_failed)
from join_util import convert_target_names,access_auto_pipeline_dataset,read_csv_target
from gpt import chat_with_gpt, gpt4_sql_script
from join import validation
import logging
from io import StringIO

logging.basicConfig(filename='auto_pipeline_join_valid_latest4.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_datetime(obj):
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def convert_excel_to_json(excel_file_path, json_file_path):
    # Read the Excel file
    xls = pd.ExcelFile(excel_file_path)

    # Specify the columns to include in the JSON file
    columns_to_include = [
        "Folder Name",
        "Target Data Name",
        "Target Data Schema",
        "Source Data Name",
        "Source Data Schema",
        "Target Data Description",
        "3 Samples of Source Data"]

    # Read the specified columns from the first sheet
    data_to_convert = pd.read_excel(xls, sheet_name='Sheet2', usecols=columns_to_include)

    # Fill missing values in the specified columns by forward filling
    columns_to_fill = ["Target Data Name"]
    data_to_convert[columns_to_fill] = data_to_convert[columns_to_fill].ffill()

    # Create a dictionary to store the groupings
    json_data_grouped = {}

    # Iterate through each row and append to the corresponding list in the dictionary
    for _, row in data_to_convert.iterrows():
        target_data_name = row["Target Data Name"]
        row_dict = row.to_dict()

        if target_data_name not in json_data_grouped:
            json_data_grouped[target_data_name] = []

        json_data_grouped[target_data_name].append(row_dict)

    # Open the JSON file for writing
    with open(json_file_path, 'w') as json_file:
        json_file.write(json.dumps(json_data_grouped, indent=4, default=convert_datetime))

    print(f"JSON file has been saved to {json_file_path}")

def create_sample_i(samples):
    sample_i = {f"sample_{i}": sample for i, sample in enumerate(samples)}
    return sample_i

def generate_prompt_auto_pipeline(no_of_source_tables,source_names,target_name,source_data_schema,
                                  target_data_schema,target_data_description,samples,test_0_path,test_1_path,
                                  sub_folder,template_option):
    target_name = target_name[0] 
    no_of_source_tables = no_of_source_tables
    source_data_schema = source_data_schema
    target_data_schema = target_data_schema[0]
    target_data_description = target_data_description[0]
    sample_i = create_sample_i(samples)
    sample_0 = sample_i.get("sample_0")
    sample_1 = sample_i.get("sample_1")

    _no_psql_meta = (
        "IMPORTANT: this script will be executed programmatically over a database "
        "driver connection (psycopg2), NOT through the interactive `psql` shell. "
        "Only output standard SQL statements. Do NOT use `psql` meta-commands "
        "(anything starting with a backslash, e.g. \\copy, \\set, \\i) — those only "
        "work inside the interactive psql client and will fail here. To load a CSV "
        "file, use the standard SQL statement: "
        "COPY <table> FROM '<absolute path>' WITH (FORMAT csv, HEADER true);"
    )

    _safe_types = (
        "IMPORTANT: the sample rows below are only a small preview — the full CSV file "
        "being loaded may contain longer text values than these samples suggest. Do NOT "
        "infer a tightly-sized type like VARCHAR(3) from the samples (e.g. picking "
        "VARCHAR(3) because a sample value is 'Sun' would break on a real value like "
        "'Thur'). For any text/string column, use TEXT (or a generously-sized VARCHAR, "
        "e.g. VARCHAR(255)) instead of guessing an exact character length."
    )

    if no_of_source_tables == 1 and template_option == 4:
        prompt = f"""
        You are a SQL developer. Please generate a Postgres sql script to convert the {no_of_source_tables} source table to be consistent with the format of the target table {target_name}. 
        {_no_psql_meta}
        {_safe_types}
        First, you must create {no_of_source_tables} source table with following {source_names} with only the given attributes: {source_data_schema}. 
        Please delete the table before creating it if the first table exists.
        Source table samples are as follows {sample_0}.
        Second, load the entire csv file with headers from the given path {test_0_path} into the {no_of_source_tables} source table respectively (treat empty value as NULL), using the SQL COPY statement described above:
        Third, you must create a target table named {target_name} with only the given attributes: {target_data_schema}. 
        Please delete the table before creating it if the first table exists.
        Hint-1: {target_data_description}
        Finally, insert all rows from the source table into only one {target_name}, note that the selection clause in the insert statement should ignore attributes that are not needed.
        Please don't remove the any table, because we need it for validation.
        Please quote the returned SQL script between "```sql\n" and "\n```".
        """
    elif no_of_source_tables == 2 and template_option == 4:
        prompt = f"""You are a SQL developer. Please generate a Postgres sql script to convert the {no_of_source_tables} source table to be consistent with the format of the target table {target_name}. 
        {_no_psql_meta}
        {_safe_types}
        First, you must create the {no_of_source_tables} tables with following {source_names} with only the given attributes respectively: {source_data_schema}. 
        Please delete the table before creating it if the first table exists.
        First table samples are as follows {sample_0} and Second table samples are as follows {sample_1}.
        Second, load the entire csv files with headers from the given paths {test_0_path} and {test_1_path} into the {no_of_source_tables} tables respectively (treat empty value as NULL), using the SQL COPY statement described above:
        Third, you must create a target table named {target_name} with only the given attributes: {target_data_schema}. 
        Please delete the table before creating it if the first table exists.
        Hint-1: {target_data_description}
        Finally, join all rows from the {no_of_source_tables} tables into only one {target_name}, note that the selection clause in the insert statement should ignore attributes that are not needed.
        Please don't remove the any table, because we need it for validation.
        Please quote the returned SQL script between "```sql\n" and "\n```". 
        """
    else:
        raise ValueError(
            f"No prompt template for {no_of_source_tables} source table(s) with "
            f"template_option={template_option}. Templates only cover 1-2 source "
            f"tables; this case has {no_of_source_tables}."
        )
    return prompt

def gpt_auto_pipeline(json_file_path, target_data_name_to_find):
    with open(json_file_path, 'r') as file:
        data_list = json.load(file)
    target_data_names = []
    source_data_names = []
    source_data_schema = []
    target_data_schema = []
    target_data_description = []
    samples = []
    for target_key, target_values in data_list.items():
        for target_value in target_values:
            if target_value.get("Target Data Name") == target_data_name_to_find:
                target_data_names.append(target_value.get("Target Data Name"))
                source_data_names.append(target_value.get("Source Data Name"))
                source_data_schema.append(target_value.get("Source Data Schema"))
                target_data_schema.append(target_value.get("Target Data Schema"))
                target_data_description.append(target_value.get("Target Data Description"))
                samples.append(target_value.get("3 Samples of Source Data"))
                #ground_truth_sql_result.append(target_value.get("Ground Truth SQL"))
    return target_data_names, source_data_names,source_data_schema, target_data_schema, target_data_description,samples


def main(*args, benchmark_dir=None):
    """Returns a list of (case_path, is_correct, case_accuracy) for every case
    attempted, so callers can report a real validation success rate instead of
    just whether an exception was raised."""
    (json_file_path, template_option, target_id, max_target_id,length_id) = args
    conn = create_connection()
    results = []

    while target_id <= max_target_id:
        target_data_name_to_find = "Target" + str(length_id) + "_" + str(target_id)
        # Get JSON data for prompt
        target_data_names, source_data_names,source_data_schema, target_data_schema, target_data_description,samples = gpt_auto_pipeline(json_file_path,target_data_name_to_find)
        if not target_data_names:
            raise ValueError(
                f"No case found for '{target_data_name_to_find}' in {json_file_path}. "
                "Case IDs in this benchmark are not contiguous — check "
                "autopipeline-benchmarks/github-pipelines/ or the JSON for valid IDs."
            )
        no_of_source_tables = len(source_data_names)
        find_target_name_folder = convert_target_names(target_data_names[0])
        main_folder_name,sub_folder, test_0_path, test_1_path, target_path = access_auto_pipeline_dataset(
            find_target_name_folder, main_folder_name=benchmark_dir
        )
        logging.info(f"target_data_name, Source_data_names: {target_data_names[0]}, {source_data_names}")
        logging.info(f"number of sources: {len(source_data_names)}")
        no_of_source_tables = len(source_data_names)
        logging.info(f"source data schema: {source_data_schema}")
        logging.info(f"target data schema:{target_data_schema}")
        # Create a list to store similarity scores of each iteration
        all_similarity_scores = []

        # Iterative Prompt Optimization and Validation
        iteration_count = 0
        validation_table_created = False
        accuracy_list = []
        # Run the experiment
        chatgpt_prompt = generate_prompt_auto_pipeline(no_of_source_tables,source_data_names,
                                                           target_data_names,source_data_schema, target_data_schema,
                                                           target_data_description,samples,test_0_path,test_1_path,sub_folder,template_option)
  
        logging.info(f"final prompt: {chatgpt_prompt}")
        #gpt_output = chat_with_gpt(chatgpt_prompt)
        total_tokens=10000
        gpt_output = gpt4_sql_script(chatgpt_prompt, total_tokens)
        logging.info(f"gold gpt sql: {gpt_output}")
        # Execute the SQL script on the specified table
        sql_result = execute_sql(conn, gpt_output)
        if isinstance(sql_result, str):
            # execute_sql returns a plain string on failure (either a
            # psycopg2 error, or "target table not identified"). Fail this
            # case clearly instead of letting pd.DataFrame() crash on it.
            logging.info(f"SQL execution failed for {target_data_name_to_find}: {sql_result}")
            print(f"SQL execution failed for {target_data_name_to_find}: {sql_result}")
            log_experiment_failed(target_data_names, target_data_name_to_find, iteration_count, [], [0.0])
            results.append((f"{length_id}_{target_id}", False, 0.0))
            target_id += 1
            continue
        sql_result_df = pd.DataFrame(sql_result)
        logging.info(f"SQL Result: {sql_result}")
        logging.info(f"sql_result_df {sql_result_df}")
        sql_result_df_sort = sql_result_df.sort_values(by=list(sql_result_df.columns))
        logging.info(f"sql_result_df_sort {sql_result_df_sort}")
        
        logging.info(f"target path: {target_path}")
        logging.info(f"{main_folder_name}{sub_folder}{target_data_name_to_find}_result.csv")
        if (validation_table_created == False):
            gold_target_csv = read_csv_target(target_path)
            gold_target_csv_pd = pd.read_csv(target_path)
            gold_target_csv_df = pd.DataFrame(gold_target_csv_pd)
            logging.info(f"gold_target_csv_df {gold_target_csv_df}")
            gold_target_csv_df_sort = gold_target_csv_df.sort_values(by=list(gold_target_csv_df.columns))
            logging.info(f"gold_target_csv_df_sort {gold_target_csv_df_sort}")
            validation_table_created = True
        # Validate the ChatGPT generated SQL script
        logging.info(f"validation_table_created: {validation_table_created}")
        case_accuracy, is_correct, similarity_scores, validation_error = validation(sql_result_df_sort,gold_target_csv_df_sort)
        accuracy_list.append(case_accuracy)
        all_similarity_scores.append(similarity_scores)
        logging.info(f"is_correct and similarity_score: {is_correct} {similarity_scores}")

        if is_correct:
            log_experiment_success(target_data_names, target_data_name_to_find, iteration_count)
        else:
            log_experiment_failed(target_data_names, target_data_name_to_find, iteration_count, all_similarity_scores,accuracy_list)

        results.append((f"{length_id}_{target_id}", bool(is_correct), case_accuracy))
        target_id = target_id + 1

    print("All similarity scores saved to all_similarity_scores.log.")
    conn.close()
    return results


if __name__ == "__main__":
    # Path to the Excel file
    # excel_file_path = 'auto-pipeline-small.xlsx'
    excel_file_path = 'auto-pipeline-100.xlsx'

    # Path to save the JSON file
    json_file_path = 'auto-pipeline-100.json'

    # Call the function to perform the conversion
    convert_excel_to_json(excel_file_path, json_file_path)
    template_option = 4 
    #length{length_id}_{target_id} is length1_2
    length_id = 1 
    target_id, max_target_id = 17,17
    source_id, max_source_id = 0 , 2
    print_experiment_settings(template_option, target_id, max_target_id, source_id, max_source_id)
    logging.info(f"*********** Starting template option and target_id: {template_option},{target_id}****************")
    print(f"*Starting template option and target_id: {template_option},{target_id}")
    main(json_file_path, template_option, target_id, max_target_id,length_id)
