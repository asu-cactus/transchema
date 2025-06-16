import time
import os
import pandas as pd
import re
import traceback
import pdb

from auto_suggest_llm_util import get_filtered_functional_dependency, calculate_score
from util.utils import execute_python, get_test_info
from llm.llm_models import TokenUsageTracker, LLMClient
from validation.hard_match import compare_lists_matching
from validation.soft_match import compare_lists_matching_soft
from log_util.log_util import create_logger


def critique(args, length, id_, log_dir_, flags, is_def, operation_history):
    prompt_file = f"prompts/{args.critique_type}_critique.txt"
    with open(prompt_file, mode="r") as f:
        query = f.read()

    log_dir = log_dir_

    path_to_files = f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/"
    # Counting files starting with 'test' in this subfolder
    file_count = sum(
        1
        for _, _, files in os.walk(path_to_files)
        for file in files
        if file.startswith("test")
    )

    ##print(file_count)
    if file_count > 1:
        json_file_path = "data/chatgpt_github_ms.json"
    else:
        json_file_path = "data/chatgpt_github_ss.json"

    len_id = length
    target_id = id_
    max_target_id = id_
    main_folder = "autopipeline-benchmarks/github-pipelines"
    anon_flag = flags[2]
    fd = flags[0]
    metadata_flag = flags[1]
    len_idx_target_idx = str(len_id) + "_" + str(target_id)

    token_tracker = TokenUsageTracker()

    start_time = time.time()

    if is_def == 1:
        type_ = "DEF_CRITIQUE"
    else:
        type_ = "NEW_CRITIQUE"
    logger = create_logger(type_, log_dir, len_id, target_id, max_target_id)

    llm_client = LLMClient(model=args.model, tracker=token_tracker, logger=logger)

    # get schema
    (
        target_data_name,
        target_data_schema,
        target_samples,
        file_count,
        source_data_name_list,
        source_data_schema_list,
        source_samples_list,
    ) = get_test_info(json_file_path, len_idx_target_idx, main_folder, anon_flag)

    # get target examples
    ground_truth_location = (
        "{main_folder}/length{len_idx_target_idx}/target.csv".format(
            main_folder=main_folder, len_idx_target_idx=len_idx_target_idx
        )
    )
    df_ground_truth = pd.read_csv(ground_truth_location, low_memory=False)
    df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)
    df_ground_truth_fd = df_ground_truth.sample(
        n=min(10, df_ground_truth.shape[0]), replace=False
    )
    target_samples = df_ground_truth_fd.values.tolist()
    target_samples = str(target_samples)
    # #print(target_samples)
    target_samples = target_samples.replace(" ,", " , ")
    target_samples = target_samples.replace("],", "],\n")

    """
    #print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    #print(target_data_schema)
    #print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    """
    query = query.replace("$SCHEMA$", target_data_schema)
    query = query.replace("$EXAMPLES$", target_samples)
    if fd == 1:
        df_ground_truth_fd = df_ground_truth.sample(
            n=min(1000, df_ground_truth.shape[0]), replace=False
        )
        df_ground_truth_fd = df_ground_truth_fd.iloc[:, :15]
        key, fd__ = get_filtered_functional_dependency(df_ground_truth_fd)
        # fd_hints = get_fd_hints(key,fd__)
        fd_hints = "Keys : " + str(key) + "\n"
        fd_hints += "Functional Dependencies : " + str(fd__)
        query = query.replace("$FD_HINT$", fd_hints)
    else:
        query = query.replace("$FD_HINT$", "")

    if args.critique_type == "history":
        query = replace_source_info(
            query,
            source_data_name_list,
            source_data_schema_list,
            source_samples_list,
        )
        query = replace_history_info(query, operation_history)
        result_path = get_result_path(args, main_folder, len_idx_target_idx)
        query = replace_result_info(query, result_path)

    # Check cardinality of the target table vs. source files
    target_cardinality = (
        df_ground_truth.nunique().max()
    )  # Maximum distinct values in the target table
    group_by_hint = None  # Default: no hint

    source_cardinality_map = {}  # Track cardinalities in source files
    source_max_map = {}
    source_min_map = {}

    test_file_idx = 0

    while True:
        test_file_path = (
            "{main_folder}/length{len_idx_target_idx}/test_{idx}.csv".format(
                main_folder=main_folder,
                len_idx_target_idx=len_idx_target_idx,
                idx=test_file_idx,
            )
        )
        if not os.path.exists(test_file_path):
            break  # Stop if no more test files
        df_source = pd.read_csv(test_file_path, low_memory=False)

        i = 0
        for col in df_source.columns:
            i += 1
            if i != 1:
                if pd.api.types.is_numeric_dtype(df_source[col]):
                    col_min = df_source[col].min()
                    col_max = df_source[col].max()
                else:
                    col_min = None
                    col_max = None

                col_cardinality = df_source[col].nunique()
                if col_min in source_min_map:
                    source_min_map[col_min].append((test_file_path, col))
                else:
                    source_min_map[col_min] = [(test_file_path, col)]

                if col_max in source_max_map:
                    source_max_map[col_max].append((test_file_path, col))
                else:
                    source_max_map[col_max] = [(test_file_path, col)]

                if col_cardinality in source_cardinality_map:
                    source_cardinality_map[col_cardinality].append(
                        (test_file_path, col)
                    )
                else:
                    source_cardinality_map[col_cardinality] = [(test_file_path, col)]

        test_file_idx += 1

    # Determine group-by hint
    if target_cardinality in source_cardinality_map:
        matching_columns = source_cardinality_map[target_cardinality]
        if len(matching_columns) == 1:
            source_file, column_name = matching_columns[0]
            group_by_hint = f"Group by the column `{column_name}` in the source file `{os.path.basename(source_file)}`."
        else:
            # Find the next largest cardinality
            larger_cardinalities = [
                key for key in source_cardinality_map if key > target_cardinality
            ]
            if larger_cardinalities:
                next_largest_cardinality = min(larger_cardinalities)
                matching_columns = source_cardinality_map[next_largest_cardinality]
                if matching_columns:
                    source_file, column_name = matching_columns[
                        0
                    ]  # Pick the first match
                    group_by_hint = f"Group by the column `{column_name}` in the source file `{os.path.basename(source_file)}`."
    else:
        # Handle the case where no exact or larger match exists
        group_by_hint = "No suitable group-by column identified."

    # Append hint to the query
    if group_by_hint and metadata_flag:
        query += f"\n\nHint: {group_by_hint}"
    else:
        query += ""

    # to decide agg func we need to first calculate relative cardinality
    # rc = (cardinality(col in TS))/(size(col in TS))
    # Extract metadata
    def aggfunc(query, col, datatype):
        if datatype == "object":
            return "count"
        size = len(col)
        if size == 1:
            if col[0] in source_min_map:
                return "min"
            elif col[0] in source_max_map:
                return "max"
            else:
                return "count"
        cardinality = col.nunique()
        rc = cardinality / size
        # "high"
        if rc > 0.7:
            return "sum/avg"
        else:
            return "count"

    metadata = []
    i = -1

    if metadata_flag == 1:
        for col in df_ground_truth.columns:
            i += 1
            col_info = {}
            if anon_flag == 1:
                col_info["Column Name"] = "col_" + str(i)
            else:
                col_info["Column Name"] = col
            col_info["Data Type"] = str(df_ground_truth[col].dtype)

            col_info["Recommended Aggregate Function"] = aggfunc(
                query, df_ground_truth[col], col_info["Data Type"]
            )

            if pd.api.types.is_numeric_dtype(df_ground_truth[col]):
                col_info["Size"] = len(df_ground_truth[col])
                # col_info["Min Value"] = df_ground_truth[col].min()
                # col_info["Max Value"] = df_ground_truth[col].max()
                # col_info["Median Value"] = df_ground_truth[col].median()
            metadata.append(col_info)

        # Format metadata as a string
        metadata_str = ""
        for col_info in metadata:
            metadata_str += f"Column Name: {col_info['Column Name']}\n"
            metadata_str += f"Data Type: {col_info['Data Type']}\n"
            metadata_str += f"Recommended Aggregate Function: {col_info['Recommended Aggregate Function']}\n"
            if "Min Value" in col_info:
                metadata_str += f"  Size: {col_info['Size']}\n"

                # metadata_str += f"  Min Value: {col_info['Min Value']}\n"
                # metadata_str += f"  Max Value: {col_info['Max Value']}\n"
                # metadata_str += f"  Median Value: {col_info['Median Value']}\n"
            metadata_str += "\n"

    # Replace $METADATA$ in the query
    if metadata_flag == 1:
        query = query.replace("$METADATA$", metadata_str)
    else:
        query = query.replace("$METADATA$", "")
    ##print("AOUBDISAUJDAOHSDSADSALKNDLKSANDSADOSAIDJSAOIDOIASJDOSA")
    res = llm_client.gpt(query)

    logger.info(query)
    logger.info(res[0])
    cost = token_tracker.cost_summary()
    logger.info(cost)

    # #print(res[0])
    if args.intermediate_materialization or args.tree_of_thoughts:
        dir_ = f"{main_folder}/source_space/length{len_idx_target_idx}/"
    else:
        dir_ = f"{main_folder}/length{len_idx_target_idx}/"
    with open(f"{dir_}/python_recovered.py", mode="r") as f:
        python_code = f.read()
    target_location_critique = (
        f"{dir_}/target_multisource_critique_{args.critique_type}.csv"
    )
    query_generator = """Based on the Critisizer Response, can you add the response in the python code.
    Note : - Make sure to write the final output of the python code to {target_location_critique}
    - Make sure to write the python code in-between "```Python" and "```"
    - Please keep the final output columns the same as it was in the python script given. [Strictly do not add prefix or suffix to the column names]
    - You just need to apply the group by according to the criticizer response.
    - Do not use assignment operation for any column.
    Python Code : ```Python 
    {python_code}
    ```

    Criticizer Response : ```
    {res}
    ```
    """.format(
        python_code=python_code,
        target_location_critique=target_location_critique,
        res=res,
    )

    res_gen = llm_client.gpt(query_generator)

    pattern = re.compile(r"```Python(.*?)```", re.DOTALL | re.IGNORECASE)
    match = pattern.search(res_gen[0])
    script = match.group(1).strip()

    logger.info(query_generator)
    logger.info(res_gen[0])
    logger.info(token_tracker.cost_summary())
    cost = token_tracker.cost_summary()
    end_time = time.time()
    time_elapsed = end_time - start_time
    ##print(script)
    response = execute_python(script)
    logger.info(response)

    try:
        df_critique = pd.read_csv(target_location_critique, low_memory=False)
        (
            case_accuracy,
            is_correct,
            similarity_scores,
            validation_error,
        ) = compare_lists_matching(df_ground_truth, df_critique)
        # need to change the definition, the sequence in the definition is incorrect
        (
            case_accuracy_,
            is_correct_,
            similarity_scores_,
        ) = compare_lists_matching_soft(df_critique, df_ground_truth)
        ##print("ACCURATCY CBELOW ")
        eps = 0.1
        if case_accuracy_ < eps:
            case_accuracy_ = 0
        # print(f"{case_accuracy}, {is_correct}")
        logger.info(is_correct)

        score = calculate_score(df_ground_truth, df_critique)

    except Exception as e:
        is_correct = False
        is_correct_ = False
        case_accuracy_ = 0
        score = 0
        print("".join(traceback.format_exc()))
        # print("YOU ARE NOT VERY GOOD AT THIS LOL")

    crit_info = (
        is_correct,
        is_correct_,
        case_accuracy_,
        cost.get("total_cost", 0.0),
        time_elapsed,
        score,
    )
    return crit_info


def replace_source_info(
    query,
    source_data_name_list,
    source_data_schema_list,
    source_samples_list,
):
    src_schema_str = ""
    for i, (source_data_name, source_data_schema, source_samples) in enumerate(
        zip(source_data_name_list, source_data_schema_list, source_samples_list)
    ):
        src_schema_str += f"""
Source {i} Name: {source_data_name}
Source {i} Schema: {source_data_schema}
Source {i} Examples: {source_samples}

"""
    return query.replace("$SRC_INFO$", src_schema_str)


def replace_history_info(query, operation_history):
    return query.replace("$OPERATIONS$", operation_history)


def get_result_path(args, main_folder, len_idx_target_idx):

    if args.intermediate_materialization or args.tree_of_thoughts:
        result_path = f"{main_folder}/source_space/length{len_idx_target_idx}/"
        # Iterate through the intermediate files in the source_space folder and get their names
        max_step = 0
        for f in os.listdir(result_path):
            if f.startswith("intermediate"):
                step = f.lstrip("intermediate_step").rstrip(".csv")
                max_step = max(max_step, int(step))
        result_path += f"intermediate_step{max_step}.csv"
    else:
        result_path = f"{main_folder}/length{len_idx_target_idx}/target_multisource.csv"

    return result_path


def replace_result_info(query, result_path):
    # Read result file as a DataFrame and get column names to replace $RES_SCHEMA$ in the query;
    # Get first 5 rows as examples to replace $RES_EXAMPLES$ in the query
    df_result = pd.read_csv(result_path, low_memory=False)
    res_schema = ", ".join(df_result.columns)
    res_examples = df_result.head(5).to_string(index=False)
    query = query.replace("$RES_SCHEMA$", res_schema)
    query = query.replace("$RES_EXAMPLES$", res_examples)
    return query
