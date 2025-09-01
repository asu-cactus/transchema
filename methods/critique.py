import time
import os
import pandas as pd
import numpy as np
import re
import traceback
import pdb
import tiktoken
from hints.hint_v3 import get_column_equivalence
from auto_suggest_llm_util import get_source, get_target_samples, get_filtered_functional_dependency, calculate_score
from util.utils import execute_python, get_test_info
from llm.llm_models import TokenUsageTracker, LLMClient
from validation.hard_match import compare_lists_matching, is_column_numerical
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
        target_data_schema_with_types,
        target_samples,
        file_count,
        source_data_name_list,
        source_data_schema_list,
        source_samples_list,
    ) = get_test_info(json_file_path, len_idx_target_idx, main_folder, anon_flag)


    # get model encoding
    if args.model == "gpt-4.1-mini":
        # According to https://github.com/openai/tiktoken/issues/395
        encoding = tiktoken.get_encoding("o200k_base")
    elif args.model == "o4-mini" or model == "o3":
        encoding = tiktoken.get_encoding("cl100k_base")
    else:
        encoding = tiktoken.encoding_for_model(args.model)

    num_tokens = args.token_limit

    num_target_samples = args.target_length

    num_source_samples = args.source_length

    # get target examples
    target_samples = get_target_samples(main_folder, len_idx_target_idx, 0, False, num_target_samples, num_tokens, len(encoding.encode(query)), encoding)
    if (target_data_schema_with_types):
        query = query.replace("$SCHEMA$", target_data_schema_with_types)
    else:
        query = query.replace("$SCHEMA$", target_data_schema)
    query = query.replace("$EXAMPLES$", target_samples)


    # get source examples
    source_information = get_source(
                             file_count, 
                             source_data_name_list, 
                             source_data_schema_list, 
                             main_folder, 
                             len_idx_target_idx,
                             num_source_samples,
                             num_tokens,
                             encoding
                         )

    query = query.replace("$SRC_INFO$", source_information)
    ground_truth_location = (
        "{main_folder}/length{len_idx_target_idx}/target.csv".format(
            main_folder=main_folder, len_idx_target_idx=len_idx_target_idx
        )
    )
    try:
       df_ground_truth = pd.read_csv(ground_truth_location, low_memory=False)
       df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)
       query = query.replace("$NUM_TUPLES$", str(len(df_ground_truth)))
       if args.critique_type == "history":
           query = replace_history_info(query, operation_history)
           result_path = get_result_path(args, main_folder, len_idx_target_idx)
           query = replace_result_info(query, num_target_samples, result_path)
    except Exception as e:
       query = query.replace("$NUM_TUPLES$", "Last python script failed to produce any output.")

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


    if metadata_flag == 1:
        query = query.replace("$METADATA$", "If the target data schema does not make sense, please suggest new column names that better represent the semantics of the columns.")


    res = llm_client.gpt(query)

    logger.info(query)
    logger.info(res[0])
    cost = token_tracker.cost_summary()
    logger.info(cost)

    try: 
        with open(
            main_folder + "/length" + len_idx_target_idx + "/python_recovered.py", mode="r"
        ) as f:
            python_code = f.read()
    except Exception as e:
        python_code = ""
    target_location_critique = (
        main_folder
        + "/length"
        + len_idx_target_idx
        + "/target_multisource_critique_"
        + args.critique_type
        + ".csv"
    )
    query_generator = """Based on the LLM response, can you add the response in the python code.
    Note : - Make sure to write the final output of the python code to {target_location_critique}
    - Make sure to write the python code in-between "```Python" and "```"
    - Please keep the final output columns the same as it was in the python script given. [Strictly do not add prefix or suffix to the column names]
    - You just need to apply the fix according to the criticizer response.
    - Do not use assignment operation for any column.
    Python Code : ```Python 
    {python_code}
    ```

    Code fixing suggestions : ```
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
    print(script)
    response = execute_python(script)
    print(response)
    # sys.exit()
    logger.info(response)

    try:
        df_critique = pd.read_csv(target_location_critique, low_memory=False)
        (
            case_accuracy,
            is_correct,
            similarity_scores,
            shared_columns,
        ) = compare_lists_matching(df_critique, df_ground_truth)
        if (is_correct==False and len(shared_columns)>0 and len(df_ground_truth)==len(df_critique)):
            print("TRY IGNORING COLUMN HEADERS AND SORTING COLUMNS FOR BETTER COMPARISON:")
            sorted_df_critique = df_critique.sort_values(by=shared_columns)
            sorted_df_ground_truth = df_ground_truth.sort_values(by=shared_columns)
            new_header_critique = []
            for col in sorted_df_critique.columns:
                if "float" in str(sorted_df_critique[col].dtype):
                    print("is float")
                    first_three_values = sorted_df_critique[col].head(3).astype(int)
                else:
                    print("is not float")
                    first_three_values = sorted_df_critique[col].head(3)
                concatenated_header = str(first_three_values.iloc[0])+"-"+str(first_three_values.iloc[1])+"-"+str(first_three_values.iloc[2])
                new_header_critique.append(concatenated_header)
            sorted_df_critique.columns=new_header_critique
            new_header_ground_truth = []
            for col in sorted_df_ground_truth.columns:
                if "float" in str(sorted_df_ground_truth[col].dtype):
                    print("is float")
                    first_three_values = sorted_df_ground_truth[col].head(3).astype(int)
                else:
                    print("is not float")
                    first_three_values = sorted_df_ground_truth[col].head(3)
                concatenated_header = str(first_three_values.iloc[0])+"-"+str(first_three_values.iloc[1])+"-"+str(first_three_values.iloc[2])
                new_header_ground_truth.append(concatenated_header)
            sorted_df_ground_truth.columns=new_header_ground_truth
            print("OUR RESPONSE:")
            print(sorted_df_critique)
            print("GROUND TRUTH:")
            print(sorted_df_ground_truth)
            (
                case_accuracy,
                is_correct,
                similarity_scores,
                shared_columns,
            ) = compare_lists_matching(sorted_df_critique, sorted_df_ground_truth)
            score = calculate_score(sorted_df_ground_truth, sorted_df_critique)
        else:
            score = calculate_score(df_ground_truth, df_critique)
        logger.info(is_correct)

    except Exception as e:
        is_correct = False
        score = 0
        print("".join(traceback.format_exc()))

    crit_info = (
        is_correct,
        cost.get("total_cost", 0.0),
        time_elapsed,
        score,
    )
    return crit_info



def replace_history_info(query, operation_history):
    return query.replace("$OPERATIONS$", operation_history)


def get_result_path(args, main_folder, len_idx_target_idx):

    if args.intermediate_materialization:
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


def replace_result_info(query, num_result_samples, result_path):
    # Read result file as a DataFrame and get column names to replace $RES_SCHEMA$ in the query;
    # Get first batch of rows as examples to replace $RES_EXAMPLES$ in the query
    df_result = pd.read_csv(result_path, low_memory=False)
    res_schema = ", ".join(df_result.columns)
    res_examples = df_result.head(num_result_samples).to_string(index=False)
    query = query.replace("$RES_SCHEMA$", res_schema)
    query = query.replace("$NUM_RES_TUPLES$", str(len(df_result)))
    query = query.replace("$RES_EXAMPLES$", res_examples)
    return query
