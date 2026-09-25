import os
import logging
import json
import pandas as pd
from padding_match import pad_comp
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import psycopg2
import csv
import re


# ──────────────────────────────────────────────────────────────────────────────
# Benchmark resolution -- single source of truth.
#
# The benchmark -> on-disk-root ternary used to be copy-pasted at 7 call sites across
# critique_data.py and methods/{single_step_cot,multi_step,critique}.py. mcts_search.py
# hit the failure mode that invites: when smart_building_v2 was added there, two copies
# were missed, so a recovered script silently validated against github-pipelines'
# unrelated target.csv. Resolving here means a new benchmark is one edit, not seven.


BENCHMARK_ROOTS = {
    "github": "autopipeline-benchmarks/github-pipelines",
    "monteprep": "autopipeline-benchmarks/monteprep-pipelines",
    "smart_building_v2": "autopipeline-benchmarks/smartbuilding-pipelines-v2-split",
}

BENCHMARK_CHOICES = tuple(BENCHMARK_ROOTS)


def resolve_main_folder(benchmark: str | None) -> str:
    """Map a --benchmark value to its pipelines root. Unknown/None -> github."""
    return BENCHMARK_ROOTS.get(benchmark or "github", BENCHMARK_ROOTS["github"])


def resolve_case_json(benchmark: str | None, file_count: int) -> str:
    """Map (benchmark, source-file count) to the case-metadata JSON.

    smart_building_v2 is single-source only, so it has no _ms variant -- passing a
    file_count > 1 there still resolves to the ss file rather than a missing path.
    """
    bm = benchmark or "github"
    if bm == "smart_building_v2":
        return "data/chatgpt_smartbuilding_v2_ss.json"
    stem = "monteprep" if bm == "monteprep" else "github"
    return f"data/chatgpt_{stem}_{'ms' if file_count > 1 else 'ss'}.json"


def drop_leading_index_col_if_present(df: pd.DataFrame) -> pd.DataFrame:
    """Drop the first column only if it's a throwaway pandas index column
    (unnamed, or literally "Unnamed: 0"), in place, and return df.

    github/monteprep target.csv files carry a leading index column like this;
    smartbuilding target.csv files do not (their first column is real data,
    e.g. "CST"/"date") and must be left untouched.
    """
    first_col = str(df.columns[0])
    if first_col == "" or first_col.startswith("Unnamed:"):
        df.drop(columns=df.columns[0], axis=1, inplace=True)
    return df


def convert_if_number(s):
    if s is None:
        return None
    try:
        return float(s)
    except ValueError:
        return s

def are_elements_equal(elem1, elem2, tolerance=1e-1):
    elem1 = "" if elem1 is None else elem1
    elem2 = "" if elem2 is None else elem2
    elem1, elem2 = convert_if_number(elem1), convert_if_number(elem2)
    if isinstance(elem1, float) and isinstance(elem2, float):
        # Following AutoPipeline's logic for checking numerical closeness
        # abs(i2-i1) != 0 and abs(i2-i1) / max(abs(i2),abs(i1)) > 0.1 gathered from column_summary.py 
        # return abs(elem1 - elem2) < tolerance
        return (abs(elem1 - elem2) / max(abs(elem1), abs(elem2))) < tolerance
    elif isinstance(elem1, str) and isinstance(elem2, str):
        return elem1.strip().lower() == elem2.strip().lower()
    else:
        return elem1 == elem2

def convert_target_names(target_names_str):
    target_names = target_names_str.split(",")
    converted_names = []

    for target_name in target_names:
        match = re.match(r"^Target(\d+)_(\d+)$", target_name.strip())
        if match:
            number1, number2 = match.groups()
            converted_name = f"length{number1}_{number2}"
            converted_names.append(converted_name)
        else:
            converted_names.append(target_name)

    converted_names_str = ", ".join(converted_names)
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
    with open(target, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            gold_target.append(tuple(row))
    return gold_target

def read_csv_file(file_path):
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        data = list(reader)
    return data


def create_connection():
    """create a database connection to the PostgreSQL database"""
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",  # e.g., "localhost"
        port="5432",  # e.g., "5432"
    )
    #print("Postgres connection established.")
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
                result = (
                    "Error:　Table name not identified from last INSERT INTO query."
                )
        else:
            result = cursor.fetchall()

        return result
    except psycopg2.Error as e:
        conn.rollback()  # Rollback the transaction on error
        return f"Error: {e.pgerror}"


def execute_python(gpt_response):
    try:
        exec(gpt_response, {"__name__": "__main__"})
        return "Success"
    except Exception as e:
        print("Exception: "+str(e))
        return f"Error: {e}"


def make_test_validation_script(script: str) -> str:
    """Swap training_X.csv → test_X.csv and redirect output to a _test_val variant.

    The output redirect preserves the training-data CSV so scoring (reward) still
    reads the training output while is_correct is computed on test output.
    Covers all target_multisource* variants: plain, _cot, _critique_history, etc.
    """
    swapped = re.sub(r'training_(\d+)\.csv', r'test_\1.csv', script)
    # Some generated scripts read training data via glob.glob(".../training_*.csv")
    # rather than a literal training_N.csv path -- the digit-only regex above misses
    # that entirely, so the "test validation" run silently kept reading TRAINING data
    # and got compared against the TEST target, producing a false is_correct=False for
    # an otherwise-correct script. Confirmed via a direct MCTS log audit (2026-09-17,
    # cases 1_2/1_3 of smartbuilding_v2_mcts20_dmx_hintsalign_t600_dmx-gpt-oss-120b):
    # the selected best script in both cases used this glob pattern, ran correctly
    # against real test data once patched, yet was recorded incorrect before this fix.
    swapped = re.sub(r'training_\*\.csv', 'test_*.csv', swapped)
    swapped = re.sub(r'(target_multisource[^.]*?)\.csv', r'\1_test_val.csv', swapped)
    return swapped


# def create_table(conn, create_statement):
#     #print(create_statement)
#     cursor = conn.cursor()
#     try:
#         cursor.execute("BEGIN;")
#         cursor.execute(create_statement)
#         # Assuming you want to commit after every SQL execution for simplicity
#         conn.commit()
#     except psycopg2.Error as e:
#         conn.rollback()  # Rollback the transaction on error
#         return f"Error: {e.pgerror}"


def log_experiment_settings(
    len_id, max_len_id, target_id, max_target_id, method, clarify_on
):
    log_directory = os.path.join(".", "log")
    os.makedirs(log_directory, exist_ok=True)
    log_file_path = os.path.join(log_directory, "all_similarity_scores.log")

    with open(log_file_path, "a+") as file:
        file.write(
            f"{'[Clarify On]' if clarify_on else '[Clarify Off]'}"
            f"{f' using {method}'}\n"
        )
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


def log_experiment_failed(
    target_data_name,
    source_data_name_to_find,
    iteration_count,
    all_similarity_scores,
    accuracy_list,
    validation_error_list,
):
    #print("[FAILED] Maximum iterations reached without correct result.")
    log_directory = os.path.join(".", "log")
    os.makedirs(log_directory, exist_ok=True)

    log_file_path = os.path.join(log_directory, "all_similarity_scores.log")
    with open(log_file_path, "a+") as file:
        file.write(f"{target_data_name} <- {source_data_name_to_find}")
        file.write("\t\t\t\t[Failed]\n\tPlease check the similarity scores:\n")
        for count, iteration_scores in enumerate(all_similarity_scores):
            file.write(f"\t\t iter-{count + 1}: ")
            if iteration_scores[0] == "mismatch":
                file.write(f"mis-match: {validation_error_list[count]}\n")
            else:
                file.write(", ".join(map(str, iteration_scores)) + "\n")
        #print(accuracy_list)
        file.write(f"\t\t\t\tCase accuracy: {max(accuracy_list):.2f}\n")


def log_experiment_success(target_data_name, source_data_name_to_find, iteration_count):
    #print("[Success] Successful SQL execution with correct result.")
    log_directory = os.path.join(".", "log")
    os.makedirs(
        log_directory, exist_ok=True
    )  # Create the directory if it doesn't exist, ignore error if it does

    log_file_path = os.path.join(log_directory, "all_similarity_scores.log")
    try:
        with open(log_file_path, "a+") as file:
            file.write(
                f"{target_data_name} <- {source_data_name_to_find} with iter-{iteration_count}\t\t[Success]\n"
            )
    except Exception as e:
        print(f"Error writing to log file: {e}")

    # with open(log_file_path, 'a+') as file:
    #     file.write(f"{target_data_name} <- {source_data_name_to_find} with iter-{iteration_count}\t\t[Success]\n")
    # Append the global accuracy to the end
    # file.write(f", Global accuracy: {case_accuracy:.2f}\n")


def log_experiment(
    target_data_name,
    source_data_name_to_find,
    execution_time_1,
    execution_time_2,
    execution_time_3,
    execution_time,
    cost,
    success,
    method,
):
    file_path = f"log/{method}.log"
    with open(file_path, "a+") as file:
        if success:
            #print(cost)
            file.write(
                f"{target_data_name} <- {source_data_name_to_find} Successful with Total time:{execution_time}(Generating Prompt time:{execution_time_1},GPT Reaction time:{execution_time_2}，SQL Execution time:{execution_time_3}) and cost:{cost}\n"
            )
        else:
            print(cost)
            file.write(
                f"{target_data_name} <- {source_data_name_to_find} Failed with Total time:{execution_time}(Generating Prompt time:{execution_time_1},GPT Reaction time:{execution_time_2}，SQL Execution time:{execution_time_3})  and cost:{cost}\n"
            )


def numerical_similarity(value1, value2, threshold=1e-10):
    """Calculate numerical similarity between two values."""
    if value1 in (0.0, None) and value2 in (0.0, None):
        return 1.0
    return 1.0 if abs(float(value1) - float(value2)) <= threshold else 0.0


def calculate_similarity(
    pred_column, gold_column, similarity_type="numerical", threshold=1e-10
):
    """Calculate similarity between two columns based on specified similarity type."""
    if similarity_type == "numerical":
        scores = [
            numerical_similarity(val1, val2, threshold)
            for val1, val2 in zip(pred_column, gold_column)
        ]
        return sum(scores) / len(scores)
    elif similarity_type == "jaccard":
        intersection = len(set(pred_column) & set(gold_column))
        union = len(set(pred_column) | set(gold_column))
        return intersection / union if union else 0
    else:  # Not used in the current version
        vectorizer = CountVectorizer().fit_transform(pred_column + gold_column)
        return cosine_similarity(
            vectorizer[: len(pred_column)], vectorizer[len(pred_column) :]
        )[0, 0]




def numerical_similarity(num1, num2, threshold=1e-8):
    return abs(num1 - num2) < threshold

#adding code to anonymize target data schema (column names)
def anonymize_target_data_schema(target_data_schema):
    # Replace column names with generic names
    target_data_schema_list = target_data_schema.split(",")
    anonymized_schema = [f"col_{i}" for i in range(len(target_data_schema_list))]
    strigifiedschema = ",".join(anonymized_schema)
    return strigifiedschema

def get_test_info(json_file_path, len_id_target_id, main_folder_path, anon_flag, data_split="test"):

    # Read the JSON file once
    with open(json_file_path, "r") as file:
        data_list = json.load(file)
        # Create a dictionary for faster lookups
        data_dict = {item["Source Data Name"]: item for item in data_list}

    # Constructing the path to the specific subfolder
    sub_folder_name = f"length{len_id_target_id}"

    #print(sub_folder_name)

    main_folder_name = os.path.abspath(main_folder_path)
    sub_folder_path = os.path.join(main_folder_name, sub_folder_name)

    # Counting files starting with data_split prefix in this subfolder (root only, no subdirs)
    file_count = sum(
        1
        for file in os.listdir(sub_folder_path)
        if file.startswith(data_split) and os.path.isfile(os.path.join(sub_folder_path, file))
    )


    # Find and store the required data
    source_data_name_list = []
    source_data_schema_list = []
    source_num_tuples = []
    source_samples_list = []
    target_data_name, target_data_schema, target_data_schema_with_types, target_samples = None, None, None, None

    for i in range(file_count):
        source_data_name_to_find = f"Source{len_id_target_id}_{i}"
        data = data_dict.get(source_data_name_to_find)

        if data:
            # Extract the relevant information from the JSON data
            if (
                target_data_name is None
            ):  # Assuming all target data names and schemas are the same
                target_data_name = data["Target Data Name"]
                target_data_schema = data["Target Data Schema"]
                target_data_schema_with_types = data["Target Data Schema with Types"]
                #adding code to anonymize target data schema (column names)
                #anonymizes on flag condition
                if(anon_flag == 1):
                    target_data_schema = anonymize_target_data_schema(target_data_schema)
                target_samples = data["Target Data Sample"]

            source_data_name_list.append(data["Source Data Name"])
            source_data_schema_list.append(data["Source Data Schema"])
            source_samples_list.append(data["3 Samples of Source Data"])

    file_count = len(source_data_name_list)

    return (
        target_data_name,
        target_data_schema,
        target_data_schema_with_types,
        target_samples,
        file_count,
        source_data_name_list,
        source_data_schema_list,
        source_samples_list,
    )
