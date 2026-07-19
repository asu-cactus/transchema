import os
import pandas as pd
import json
from datetime import datetime
from util import (create_connection, execute_sql, print_experiment_settings,
                   log_experiment_success, log_experiment_failed)
from join_util import convert_target_names,access_auto_pipeline_dataset,read_csv_target
from gpt import chat_with_gpt, gpt4_sql_script
from join import validation
from prepare_transchema_json import read_schema_and_samples
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
                                  target_data_schema,target_data_samples,target_data_description,
                                  samples,test_0_path,test_1_path,sub_folder,template_option):
    target_name = target_name[0] 
    no_of_source_tables = no_of_source_tables
    source_data_schema = source_data_schema
    target_data_schema = target_data_schema[0]
    target_data_sample = target_data_samples[0]
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
        Representative target rows are: {target_data_sample}
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
        Representative target rows are: {target_data_sample}
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
    target_data_samples = []
    target_data_description = []
    samples = []
    for target_key, target_values in data_list.items():
        for target_value in target_values:
            if target_value.get("Target Data Name") == target_data_name_to_find:
                target_data_names.append(target_value.get("Target Data Name"))
                source_data_names.append(target_value.get("Source Data Name"))
                source_data_schema.append(target_value.get("Source Data Schema"))
                target_data_schema.append(target_value.get("Target Data Schema"))
                target_data_samples.append(target_value.get("Target Data Sample", ""))
                target_data_description.append(target_value.get("Target Data Description"))
                samples.append(target_value.get("3 Samples of Source Data"))
                #ground_truth_sql_result.append(target_value.get("Ground Truth SQL"))
    return (
        target_data_names, source_data_names, source_data_schema,
        target_data_schema, target_data_samples, target_data_description, samples
    )


def main(*args, benchmark_dir=None, max_iterations=5):
    """Returns a list of (case_path, is_correct, case_accuracy) for every case
    attempted, so callers can report a real validation success rate instead of
    just whether an exception was raised."""
    (json_file_path, template_option, target_id, max_target_id,length_id) = args
    conn = create_connection()
    results = []

    while target_id <= max_target_id:
        target_data_name_to_find = "Target" + str(length_id) + "_" + str(target_id)
        # Get JSON data for prompt
        (
            target_data_names, source_data_names, source_data_schema,
            target_data_schema, target_data_samples, target_data_description,
            samples
        ) = gpt_auto_pipeline(json_file_path, target_data_name_to_find)
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

        # Transchema's metadata JSON strips pandas' unnamed index column from
        # "Source Data Schema" (fine for its own pandas-based pipeline, which
        # can just drop that column). SQLMorpher instead has the model write a
        # raw SQL `COPY ... FROM <csv>`, which loads the file byte-for-byte —
        # so the CREATE TABLE column count MUST match the real file exactly,
        # or COPY fails with "extra data after last expected column". Override
        # the schema/samples shown to the model with what's actually on disk.
        for i, source_path in enumerate([test_0_path, test_1_path][:no_of_source_tables]):
            try:
                real_schema, real_samples = read_schema_and_samples(source_path)
                source_data_schema[i] = str(real_schema)
                samples[i] = str(real_samples)
            except Exception as e:
                logging.info(f"Could not read real schema for {source_path}: {e}")

        # The target's leading CSV index is only a serialization artifact and
        # is not part of the logical target schema. Normalize this on every
        # run so stale synthesized JSON caches cannot reintroduce it.
        try:
            real_target_schema, _ = read_schema_and_samples(target_path)
            logical_target_schema = [
                col for col in real_target_schema
                if not str(col).startswith("Unnamed:")
            ]
            target_data_schema[0] = str(logical_target_schema)
        except Exception as e:
            logging.info(f"Could not read real target schema for {target_path}: {e}")

        logging.info(f"target_data_name, Source_data_names: {target_data_names[0]}, {source_data_names}")
        logging.info(f"number of sources: {len(source_data_names)}")
        no_of_source_tables = len(source_data_names)
        logging.info(f"source data schema: {source_data_schema}")
        logging.info(f"target data schema:{target_data_schema}")
        # Create a list to store similarity scores of each iteration
        all_similarity_scores = []
        accuracy_list = []

        base_prompt = generate_prompt_auto_pipeline(
            no_of_source_tables, source_data_names, target_data_names,
            source_data_schema, target_data_schema, target_data_samples,
            target_data_description, samples, test_0_path, test_1_path,
            sub_folder, template_option
        )

        # Benchmark CSVs contain a pandas-generated leading index column
        # ("Unnamed: 0"), but the benchmark target schema intentionally omits
        # it. Compare against the logical target table, not that serialization
        # artifact; otherwise every otherwise-correct result has one fewer
        # column and can never pass.
        gold_target_csv_df = pd.read_csv(target_path, low_memory=False)
        unnamed_columns = [
            col for col in gold_target_csv_df.columns
            if str(col).startswith("Unnamed:")
        ]
        if unnamed_columns:
            gold_target_csv_df.drop(columns=unnamed_columns, inplace=True)
        gold_target_csv_df_sort = gold_target_csv_df.sort_values(
            by=list(gold_target_csv_df.columns)
        ).reset_index(drop=True)
        logging.info(f"gold_target_csv_df_sort {gold_target_csv_df_sort}")

        retry_feedback = ""
        is_correct = False
        case_accuracy = 0.0

        for iteration_count in range(1, max_iterations + 1):
            print(
                f"Attempt {iteration_count}/{max_iterations} for "
                f"{target_data_name_to_find}"
            )
            chatgpt_prompt = base_prompt + retry_feedback
            logging.info(f"final prompt attempt {iteration_count}: {chatgpt_prompt}")

            gpt_output = gpt4_sql_script(chatgpt_prompt, total_tokens=10000)
            logging.info(f"generated SQL attempt {iteration_count}: {gpt_output}")
            sql_result = execute_sql(conn, gpt_output)

            if isinstance(sql_result, str):
                accuracy_list.append(0.0)
                all_similarity_scores.append(["sql_execution_error"])
                print(
                    f"SQL execution failed for {target_data_name_to_find} "
                    f"(attempt {iteration_count}/{max_iterations}): {sql_result}"
                )
                retry_feedback = f"""

The previous SQL attempt failed to execute.
Previous SQL:
```sql
{gpt_output}
```
PostgreSQL error:
{sql_result}
Return a complete corrected SQL script. Follow all original constraints.
"""
                continue

            sql_result_df = pd.DataFrame(sql_result)
            sql_result_df_sort = sql_result_df.sort_values(
                by=list(sql_result_df.columns)
            ).reset_index(drop=True)
            logging.info(f"sql_result_df_sort {sql_result_df_sort}")

            case_accuracy, is_correct, similarity_scores, validation_error = validation(
                sql_result_df_sort, gold_target_csv_df_sort
            )
            accuracy_list.append(case_accuracy)
            all_similarity_scores.append(similarity_scores)
            logging.info(
                f"attempt={iteration_count} is_correct={is_correct} "
                f"similarity={similarity_scores} error={validation_error}"
            )

            if is_correct:
                log_experiment_success(
                    target_data_names, target_data_name_to_find, iteration_count
                )
                break

            retry_feedback = f"""

The previous SQL executed, but its result did not match the required target.
Previous SQL:
```sql
{gpt_output}
```
Validation feedback: {validation_error or similarity_scores}
Generated result shape: {sql_result_df.shape}
Expected result shape: {gold_target_csv_df.shape}
Return a complete revised SQL script that corrects the transformation. Follow
all original constraints. Do not return only a patch or explanation.
"""

        if not is_correct:
            log_experiment_failed(
                target_data_names, target_data_name_to_find, max_iterations,
                all_similarity_scores, accuracy_list
            )

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
