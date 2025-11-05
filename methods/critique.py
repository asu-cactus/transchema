import time
import os
import pandas as pd
import numpy as np
import re
import traceback
import tiktoken
from hints.hint_v3 import get_column_equivalence
from auto_suggest_llm_util import get_source, get_target_samples, get_filtered_functional_dependency, calculate_score
from util.utils import execute_python, get_test_info
from llm.llm_models import TokenUsageTracker, LLMClient
from validation.hard_match import compare_lists_matching, is_column_numerical
from validation.soft_match import compare_lists_matching_soft
from log_util.log_util import create_logger

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
from rag_pipeline.rag_layer import RAGDB, milvus_results_to_json


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
    # anon_flag = flags[2]
    # fd = flags[0]
    # metadata_flag = flags[1]
    # few_shot_flag = flags[3]

    fd, metadata_flag, anon_flag, few_shot_flag = flags
    
    len_idx_target_idx = str(len_id) + "_" + str(target_id)


    token_tracker = TokenUsageTracker()

    start_time = time.time()

    if is_def == 1:
        type_ = "DEF_CRITIQUE"
    else:
        type_ = "NEW_CRITIQUE"
    
    logger = create_logger(type_, log_dir, len_id, target_id, max_target_id)
    
    llm_client = LLMClient(model=args.model, tracker=token_tracker, logger=logger)
    
    # Inserting components for Few Shot examples here:

    rag_db = None
    if args.few_shot:

        rag_db = RAGDB(
            uri= args.rag_db_uri, # "rag_pipeline/test_dummy/milvus_demo_4.db",
            model_id=args.rag_embedding_model, # "Qwen/Qwen3-Embedding-0.6B",
            collection=args.rag_db_collection, #"plan_docs",
            max_len=args.rag_embedding_dim
        )
    
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
    elif args.model == "o4-mini" or args.model == "o3":
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
    

    if few_shot_flag == 1:        
        aux_query = query if isinstance(query, list) else [query]
        rag_results = rag_db.search(
            aux_query, 
            top_k=args.rag_topk, 
            batch_size=args.rag_embedding_batch_size
        )

        # This is a comma separated string,
        # therefore splitting it before passing it into a function.

        output_fields = args.rag_output_fields.split(",")

        rag_json_results = milvus_results_to_json(
            results=rag_results, 
            output_fields=output_fields
        )
        
        few_shot_docs = [f"Few-shot Example {idx}:\n {document['doc']}" for idx, document in enumerate(rag_json_results)]
        few_shot_prompt = "\n\n".join(few_shot_docs)
        few_shot_prompt = "Here are some few shot examples:\n\n" + few_shot_prompt

        query = query.replace("$FEW_SHOT_EXAMPLES$", few_shot_prompt)


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
    query_generator = """Based on the LLM response, can you refine the python code.

Hint 1:
Note that some column names, e.g., purpose, funded_year, may not match the values in the column, e.g., 5 for purpose, 16844 for funded_year. In this case consider the column to be aggregation, e.g., count per purpose, and sum for funded_year. They should not be used in Group By columns.

Hint 2:
If the resulting data generated by the failed Python script has the same schema with the available target examples, but has more rows, it may indicate the following: (1) A Group By operator and Aggregate operators are missing. We would suggest adding a Group By operator using the left-most non-float, and unique attributes from the given target examples as GroupBy attributes and choosing the Aggregation operator such as count, average, medium, sum, etc., based on the range of valuesfor each of other columns. (2) If a Group By operator has been used, we would suggest remove some Group By attributes. (3) If OUTER join is used, it should be replaced by INNER join. (4) We shall remove rows that contain NaN values.

Hint 3:
If the output data from the last generated python script has the same schema with the target examples, however the key constraints exist in the target examples do not exist in the generated output data, please add a GroupBy to the last generated python script. The GroupBy attributes must be the primary key of the target examples (i.e., attributes serving as unique tuple identifer in the target examples).

Hint 4:
If the resulting data generated by the failed Python script has the same schema with the available target examples, but has fewer rows, it may indicate the following: (1) If INNER join is used, it should be replaced by OUTER join. (2) We shall keep rows that contain NaN values. (3) If Group By is used, it should be removed or use more Group By attributes.

Hint 5:
If multiple source tables share the same schema while the target table (i.e., target examples) also has the same schema, UNION must be used. However if m source tables share the same schema consisting of k non-key columns, but the target table has renamed each non-key column shared into k different columns, and thus consists of k x m non-key columns, JOIN should be applied to join all source tables on the primary key.

Hint 5:
Group By columns are never float types. These Group By columns correspond to columns that are UNIQUE and non-float in the target examples, which are usually at the leftmost part of the columns of the target examples.

Hint 6:
If the given target examples contain duplicate keys or duplicate rows, Group By should NOT be used.

Hint 7:
If the average value of a column in the target examples is significantly bigger than its average values in the source tables, sum aggregation should be applied to the column, and this column should be excluded from the Group By columns.

Hint 8:
If a column that usually has value range (such as year or funded_year) in the target table has abnormal values (e.g., 0 or 16888 for year or XXXX_year), an aggregation should be applied to the column and this column MUST be EXCLUDED from the Group By columns.

Hint 9:
JOIN is usually applied to two tables sharing the same primary key, or applied to two tables where one table has a column (i.e., foreign key) referencing to the primary key of the other table.

Hint 10:
Two different tables may join on shared columns that have different names but contain similar values. For example, in a source table called test_0.csv, there exists a Code column containing values such as AUS, AUT, BEL, CAN, FRA, while another source table called test_1.csv contains a column Country that has values such as FRA, BEL, GRA, USA, CAN. These source tables test_0 and test_1 can be joined on test_0.Code = test_1.Country. Similarly, if test_0 has a column Country having values Afghanistan, Albania, Algeria, Angola, etc, while test_2 has a column Host having similar country values such as France, Switzerland, United States, Germany, etc, the output of test_0 and test_1 df01 could join test_2 on df01.Country = test_2.Host.

Hint 11:
IMPORTANT: NEVER use all target columns as the GROUP BY columns!!!

Hint 12:
If in the target data examples, many columns have the same constant numerical values for each tuple, it may indicate a count is used after grouping data by the key of the target examples. 

Hint 13:
If in the target data examples, many columns have similar but different numerical values such as 5 5 4 5 4, in each row, it indicates that a COUNT DISTINCT is used.

Hint 14:
If the target data examples, some columns have the same constant values for all tuples, you may simply use the same constant value in the Python script for those columns.

Hint 15:
Consider applying string functions to certain columns that look similar but have different formats in the target and resulting data examples.

Hint 16:
Please look at the target examples, and ensure the generated data has the same type and name for each column in the target examples.


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
    query = query.replace("$RES_SCHEMA_NOT_AVAILABLE$", res_schema)
    query = query.replace("$NUM_RES_TUPLES_NOT_AVAILABLE$", str(len(df_result)))
    query = query.replace("$RES_EXAMPLES_NOT_AVAILABLE$", res_examples)
    return query
