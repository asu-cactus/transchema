import os
import logging
import json


def convert_target_names(target_names_str):
    target_names = target_names_str.split(',')
    converted_names = []

    for target_name in target_names:
        match = re.match(r'^Target(\d+)_(\d+)$', target_name.strip())
        if match:
            number1, number2 = match.groups()
            converted_name = f"length{number1}_{number2}"
            converted_names.append(converted_name)
        else:
            converted_names.append(target_name)

    converted_names_str = ', '.join(converted_names)
    return converted_names_str


def access_auto_pipeline_dataset(sub_folder_name):
    main_folder_name = "github-pipelines"
    main_folder_name = os.path.abspath(main_folder_name)
    sub_folder = f"{main_folder_name}\{sub_folder_name}\\"
    test_0 = f"{sub_folder}test_0.csv"
    test_1 = f"{sub_folder}test_1.csv"
    target = f"{sub_folder}target.csv"
    return main_folder_name, sub_folder, test_0, test_1, target


def read_csv_target(target):
    gold_target = []
    logging.info(f"Final target path{target}")
    with open(target, 'r', encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            gold_target.append(tuple(row))
    return gold_target


from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import psycopg2
import csv
import re


def read_csv_file(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    return data


def create_connection():
    """ create a database connection to the PostgreSQL database """
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",  # e.g., "localhost"
        port="5432"  # e.g., "5432"
    )
    print("Postgres connection established.")
    return conn


def extract_last_insert_table_name(query):
    """
    Extracts the table name from the last INSERT INTO clause in the given SQL query.
    """
    matches = re.findall(r"INSERT\s+INTO\s+(\"[^\"]+\"|\w+)", query, re.IGNORECASE)
    if matches:
        return matches[-1]
    return None


def execute_sql(conn, query):
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN;")
        cursor.execute(query)
        # Assuming you want to commit after every SQL execution for simplicity
        conn.commit()

        # Check if the operation is not a SELECT statement
        if not query.strip().upper().startswith("SELECT"):
            target_table = extract_last_insert_table_name(query)
            if target_table:
                # Fetch results from the last inserted table
                cursor.execute(f"SELECT * FROM {target_table};")
                result = cursor.fetchall()
            else:
                result = "Error:　Table name not identified from last INSERT INTO query."
        else:
            result = cursor.fetchall()

        return result
    except psycopg2.Error as e:
        conn.rollback()  # Rollback the transaction on error
        return f"Error: {e.pgerror}"


# def create_table(conn, create_statement):
#     print(create_statement)
#     cursor = conn.cursor()
#     try:
#         cursor.execute("BEGIN;")
#         cursor.execute(create_statement)
#         # Assuming you want to commit after every SQL execution for simplicity
#         conn.commit()
#     except psycopg2.Error as e:
#         conn.rollback()  # Rollback the transaction on error
#         return f"Error: {e.pgerror}"


def log_experiment_settings(len_id, max_len_id, target_id, max_target_id, method, clarify_on):
    log_directory = os.path.join('.', 'log')
    os.makedirs(log_directory, exist_ok=True)
    log_file_path = os.path.join(log_directory, 'all_similarity_scores.log')

    with open(log_file_path, 'a+') as file:
        file.write(f"{'[Clarify On]' if clarify_on else '[Clarify Off]'}"
                   f"{f' using {method}'}\n")
        file.write("Scope: length ")
        if len_id == max_len_id:
            file.write(f"is {len_id}")
        else:
            file.write(f"in [{len_id}, {max_len_id}]")
        file.write(", target ")
        if target_id == max_target_id:
            file.write(f"is {target_id}")
        else:
            file.write(f"in [{target_id}, {max_target_id}]")
        file.write("\n")


def log_experiment_failed(target_data_name, source_data_name_to_find, iteration_count, all_similarity_scores,
                          accuracy_list, validation_error_list):
    print("[FAILED] Maximum iterations reached without correct result.")
    log_directory = os.path.join('.', 'log')
    os.makedirs(log_directory, exist_ok=True)

    log_file_path = os.path.join(log_directory, 'all_similarity_scores.log')
    with open(log_file_path, 'a+') as file:
        file.write(f"{target_data_name} <- {source_data_name_to_find}")
        file.write("\t\t\t\t[Failed]\n\tPlease check the similarity scores:\n")
        for count, iteration_scores in enumerate(all_similarity_scores):
            file.write(f"\t\t iter-{count + 1}: ")
            if iteration_scores[0] == "mismatch":
                file.write(f"mis-match: {validation_error_list[count]}\n")
            else:
                file.write(", ".join(map(str, iteration_scores)) + "\n")
        print(accuracy_list)
        file.write(f"\t\t\t\tCase accuracy: {max(accuracy_list):.2f}\n")


def log_experiment_success(target_data_name, source_data_name_to_find, iteration_count):
    print("[Success] Successful SQL execution with correct result.")
    log_directory = os.path.join('.', 'log')
    os.makedirs(log_directory, exist_ok=True)  # Create the directory if it doesn't exist, ignore error if it does

    log_file_path = os.path.join(log_directory, 'all_similarity_scores.log')
    try:
        with open(log_file_path, 'a+') as file:
            file.write(f"{target_data_name} <- {source_data_name_to_find} with iter-{iteration_count}\t\t[Success]\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")

    # with open(log_file_path, 'a+') as file:
    #     file.write(f"{target_data_name} <- {source_data_name_to_find} with iter-{iteration_count}\t\t[Success]\n")
        # Append the global accuracy to the end
        # file.write(f", Global accuracy: {case_accuracy:.2f}\n")


def numerical_similarity(value1, value2, threshold=1e-10):
    """ Calculate numerical similarity between two values. """
    if value1 in (0.0, None) and value2 in (0.0, None):
        return 1.0
    return 1.0 if abs(float(value1) - float(value2)) <= threshold else 0.0


def calculate_similarity(pred_column, gold_column, similarity_type="numerical", threshold=1e-10):
    """ Calculate similarity between two columns based on specified similarity type. """
    if similarity_type == "numerical":
        scores = [numerical_similarity(val1, val2, threshold) for val1, val2 in zip(pred_column, gold_column)]
        return sum(scores) / len(scores)
    elif similarity_type == "jaccard":
        intersection = len(set(pred_column) & set(gold_column))
        union = len(set(pred_column) | set(gold_column))
        return intersection / union if union else 0
    else:  # Not used in the current version
        vectorizer = CountVectorizer().fit_transform(pred_column + gold_column)
        return cosine_similarity(vectorizer[:len(pred_column)], vectorizer[len(pred_column):])[0, 0]


def convert_if_number(s):
    if s is None:
        return None
    try:
        return float(s)
    except ValueError:
        return s


def are_elements_equal(elem1, elem2, tolerance=1e-8):
    elem1 = '' if elem1 is None else elem1
    elem2 = '' if elem2 is None else elem2
    elem1, elem2 = convert_if_number(elem1), convert_if_number(elem2)
    if isinstance(elem1, float) and isinstance(elem2, float):
        return abs(elem1 - elem2) < tolerance
    elif isinstance(elem1, str) and isinstance(elem2, str):
        return elem1.strip().lower() == elem2.strip().lower()
    else:
        return elem1 == elem2


def numerical_similarity(num1, num2, threshold=1e-8):
    return abs(num1 - num2) < threshold


def is_column_numerically_dominant(column):
    numeric_count = 0
    for val in column:
        try:
            float(val)
            numeric_count += 1
        except (ValueError, TypeError):
            if val == '':
                numeric_count += 1  # treating empty string as valid for numeric
    return numeric_count / len(column) > 0.5  # Majority of values are numeric


def compare_columns(pred_column, gold_column, threshold=1e-8):
    # Determine if columns are numerically dominant
    is_numerical_a = is_column_numerically_dominant(pred_column)
    is_numerical_b = is_column_numerically_dominant(gold_column)

    if is_numerical_a and is_numerical_b:
        # Both columns are numerically dominant
        scores = [numerical_similarity(float(val1 or 0), float(val2 or 0), threshold)
                  for val1, val2 in zip(pred_column, gold_column)]
        return sum(scores) / len(scores)
    else:
        # For string comparison, convert strings to lower case for case-insensitive comparison
        pred_column_lower = [str(val).lower() for val in pred_column]
        gold_column_lower = [str(val).lower() for val in gold_column]

        intersection = len(set(pred_column_lower) & set(gold_column_lower))
        union = len(set(pred_column_lower) | set(gold_column_lower))
        return intersection / union if union else 0


# Main Comparison Function
def compare_lists_matching(generated_sql_df, ground_truth_df):
    generated_sql_df = generated_sql_df.sort_values(by=list(generated_sql_df.columns))
    ground_truth_df = ground_truth_df.sort_values(by=list(ground_truth_df.columns))

    if len(generated_sql_df.columns) == 0 or len(ground_truth_df.columns) == 0:
        return 0, False, ['mismatch'], ["Mismatch - No columns in one or both DataFrames"]

    if len(generated_sql_df) != len(ground_truth_df):
        return 0, False, ['mismatch'], [
            f"Mismatch - DataFrames lengths differ (pred:{len(generated_sql_df)} v.s. gold:{len(ground_truth_df)})"]

    similarities = []
    all_mismatches = []

    for col in generated_sql_df.columns:
        pred_column = generated_sql_df[col].tolist()
        gold_column = ground_truth_df[col].tolist()

        # Use the updated function to determine if the column is numerically dominant
        is_numerical = is_column_numerically_dominant(generated_sql_df[col])

        # Use the updated compare_columns function
        column_similarity = compare_columns(pred_column, gold_column)
        similarities.append(column_similarity)

        if column_similarity < 1:
            mismatches = [
                {'<col, row>': '<' + str(col) + ', ' + str(i) + '>', 'pred': pred_column[i], 'gold': gold_column[i]}
                for i in range(len(pred_column))
                if not are_elements_equal(pred_column[i], gold_column[i])]
            all_mismatches.append((col, mismatches))

    average_similarity = sum(similarities) / len(generated_sql_df.columns)
    res = average_similarity == 1

    return average_similarity, res, similarities, all_mismatches


def get_test_info(json_file_path, len_id_target_id):
    # Read the JSON file once
    with open(json_file_path, 'r') as file:
        data_list = json.load(file)
        # Create a dictionary for faster lookups
        data_dict = {item["Source Data Name"]: item for item in data_list}

    # Constructing the path to the specific subfolder
    sub_folder_name = f"length{len_id_target_id}"
    main_folder_name = os.path.abspath("github-pipelines")
    sub_folder_path = os.path.join(main_folder_name, sub_folder_name)

    # Counting files starting with 'test' in this subfolder
    file_count = sum(1 for _, _, files in os.walk(sub_folder_path) for file in files if file.startswith('test'))

    # Find and store the required data
    source_data_name_list = []
    source_data_schema_list = []
    source_samples_list = []
    target_data_name, target_data_schema, target_samples = None, None, None

    for i in range(file_count):
        source_data_name_to_find = f"Source{len_id_target_id}_{i}"
        data = data_dict.get(source_data_name_to_find)

        if data:
            # Extract the relevant information from the JSON data
            if target_data_name is None:  # Assuming all target data names and schemas are the same
                target_data_name = data["Target Data Name"]
                target_data_schema = data["Target Data Schema"]
                target_samples = data["Target Data Sample"]

            source_data_name_list.append(data["Source Data Name"])
            source_data_schema_list.append(data["Source Data Schema"])
            source_samples_list.append(data["3 Samples of Source Data"])

    return target_data_name, target_data_schema, target_samples, file_count, source_data_name_list, source_data_schema_list, source_samples_list


