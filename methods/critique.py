import time
import os
import pandas as pd
import re
import traceback
import numpy as np
from auto_suggest_llm_util import (
    get_filtered_functional_dependency,
    calculate_score)

from util.utils import execute_python, get_test_info
from llm.llm_models import TokenUsageTracker, LLMClient
import parameters as p
from validation.hard_match import compare_lists_matching
from validation.soft_match import compare_lists_matching_soft
from log_util.log_util import create_logger
import sys
from hints.hint_v3 import get_column_equivalence

def critique(args, length, id_, nature, log_dir_, flags, is_def, i_, experiment_name):
    file_path = nature
    with open(file_path, mode="r") as f:
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
    

    ##print(file_count)
    if(file_count > 1):
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
    
    if(is_def == 1):
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
    
    '''
    #print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    #print(target_data_schema)
    #print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    '''
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
        query = query.replace("$FD_HINTS$", "")


    # Check cardinality of the target table vs. source files
    target_cardinality = df_ground_truth.nunique().max()  # Maximum distinct values in the target table
    group_by_hint = None  # Default: no hint

    source_cardinality_map = {}  # Track cardinalities in source files
    source_max_map = {}
    source_min_map = {}

    test_file_idx = 0

    while True:
        test_file_path = '{main_folder}/length{len_idx_target_idx}/test_{idx}.csv'.format(
            main_folder=main_folder, len_idx_target_idx=len_idx_target_idx, idx=test_file_idx
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
                    source_cardinality_map[col_cardinality].append((test_file_path, col))
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
            larger_cardinalities = [key for key in source_cardinality_map if key > target_cardinality]
            if larger_cardinalities:
                next_largest_cardinality = min(larger_cardinalities)
                matching_columns = source_cardinality_map[next_largest_cardinality]
                if matching_columns:
                    source_file, column_name = matching_columns[0]  # Pick the first match
                    group_by_hint = (
                        f"Group by the column `{column_name}` in the source file `{os.path.basename(source_file)}`."
                    )
    else:
        # Handle the case where no exact or larger match exists
        group_by_hint = ""
    # aggregation hint
    column_set = get_column_equivalence(df_ground_truth)
    if(len(column_set) > 3) : 
        group_by_hint += f"\n Aggregate {', '.join(column_set)}, by counting them if they equal to each other: " + \
      ', '.join([f"Count(Target.{col})" for col in column_set]) + "\n"
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
            elif col[0] in source_max_map :
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
        



    def find_best_matching_col_from_source(col_name: str, length: int, id_: int):
        """
        Search through the headers of all test CSVs under:
            autopipeline-benchmarks/github-pipelines/length{length}_{id_}/test_{idx}.csv

        For each file, read only the header (no data) and look for a column name
        such that either:
        - col_name is a substring of that column name, or
        - that column name is a substring of col_name.

        As soon as a match is found, return the matching column name.
        If no match is found in any file, return None.
        """
        main_folder = "autopipeline-benchmarks/github-pipelines"
        test_file_idx = 0

        while True:
            test_file_path = os.path.join(
                main_folder,
                f"length{length}_{id_}",
                f"test_{test_file_idx}.csv"
            )

            if not os.path.exists(test_file_path):
                # No more files in this directory
                break

            # Read only the header (no rows) to get the column names
            df_source = pd.read_csv(test_file_path, low_memory=False)

            # Check each column name in this file’s header
            for src_col in df_source.columns:
                if col_name in src_col or src_col in col_name:
                    return src_col, df_source[src_col]

            test_file_idx += 1

        # If we get here, no matching column was found in any test file
        return None, None

        
    def aggfunc1(query, col_name, col, datatype, pos):
        # find best matching column from source
        matching_col_name, matching_col = find_best_matching_col_from_source(
            col_name,length, id_
        )
        if datatype == "object" or (datatype == "int64" and pos < 1 ):
                return "group_by"
        if matching_col_name is None : 
            if datatype == "float64" :
                return "sum/avg"
            elif datatype == "int64" :
                return "count/sum/min/max"
        else : 

            if matching_col.dtype == "object" and datatype == "int64":
                return "count"
            elif matching_col.dtype in ["int64", "float64"] and np.mean(col)/np.mean(matching_col) > 10:
                return "sum"
            elif matching_col.dtype in ["int64", "float64"] and np.mean(col)/np.mean(matching_col) > 0.5 and np.mean(col)/np.mean(matching_col) < 2:
                return "count/avg/min/max"
            else : 
                return "count/sum/avg/min/max"
                

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
            
            col_info["Recommended Aggregate Function"] = aggfunc1(
                query, col, df_ground_truth[col], col_info["Data Type"], i
            )

            if pd.api.types.is_numeric_dtype(df_ground_truth[col]):
                col_info['Size'] = len(df_ground_truth[col])
                #col_info["Min Value"] = df_ground_truth[col].min()
                #col_info["Max Value"] = df_ground_truth[col].max()
                #col_info["Median Value"] = df_ground_truth[col].median()
            metadata.append(col_info)

        # Format metadata as a string
        metadata_str = ""
        for col_info in metadata:
            metadata_str += f"Column Name: {col_info['Column Name']}\n"
            metadata_str += f"Data Type: {col_info['Data Type']}\n"
            if col_info['Recommended Aggregate Function'] == "group_by":
                metadata_str += "Recommended Group By Column\n\n"
            else : 
                metadata_str += f"Recommended Aggregate Function: {col_info['Recommended Aggregate Function']}\n\n"
            # if "Min Value" in col_info:
            #     metadata_str += f"  Size: {col_info['Size']}\n"

                #metadata_str += f"  Min Value: {col_info['Min Value']}\n"
                #metadata_str += f"  Max Value: {col_info['Max Value']}\n"
                #metadata_str += f"  Median Value: {col_info['Median Value']}\n"
            # metadata_str += "\n"

    # Replace $METADATA$ in the query
    if metadata_flag == 1:
        query = query.replace("$METADATA$", metadata_str)
    else:
        query = query.replace("$METADATA$", "")


    res = llm_client.gpt(query)

    logger.info(query)
    logger.info(res[0])
    cost = token_tracker.cost_summary()
    logger.info(cost)

    # #print(res[0])
    secret = nature[:2]
    with open(
        main_folder + "/length" + len_idx_target_idx + "/python_recovered.py", mode="r"
    ) as f:
        python_code = f.read()
    target_location_critique = (
        main_folder
        + "/length"
        + len_idx_target_idx
        + "/target_multisource_critique_"
        + secret
        + ".csv"
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
            validation_error,
        ) = compare_lists_matching(df_ground_truth,df_critique)
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
        #print(f"{case_accuracy}, {is_correct}")
        logger.info(is_correct)

        score = calculate_score(df_ground_truth,df_critique)
        
    except Exception as e:
        is_correct = False
        is_correct_ = False
        case_accuracy_ = 0
        score = 0
        print("".join(traceback.format_exc()))
    
    crit_info = (is_correct,is_correct_, case_accuracy_,cost.get('total_cost', 0.0),time_elapsed,score)
    return crit_info 