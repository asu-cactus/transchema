from test_scope import get_test_cases_ids
from llm.llm_models import TokenUsageTracker, LLMClient
from util.utils import get_test_info, execute_python, compare_lists_matching, compare_lists_matching_soft
from padding_match import pad_comp
import time
import auto_suggest_llm_prompts as prt
from auto_suggest_llm_util import (
    create_logger,
    get_source,
    get_operation,
    get_columns,
    get_source_with_location,
    cost_compare,
    query_gpt,
    get_columns_aggr,
    get_columns_join,
    get_prompt,
    get_filtered_functional_dependency,
    calculate_score
)
import parameters as p
import pandas as pd
import re
import sys
from pathlib import Path
import os
import traceback

from auto.main import Autologtuple,sheet_dir,creds_path, sheets

# experiment_name = ""

# flags = [anon_flag, fd_flag, md_flag]
# returns accuracy against g.t.
def critique(length, id_, nature, log_dir_, flags, is_def, i_, experiment_name):
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

    llm_client = LLMClient(model=p.model, tracker=token_tracker, logger=logger)

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
            metadata_str += f"Recommended Aggregate Function: {col_info['Recommended Aggregate Function']}\n"
            if "Min Value" in col_info:
                metadata_str += f"  Size: {col_info['Size']}\n"

                #metadata_str += f"  Min Value: {col_info['Min Value']}\n"
                #metadata_str += f"  Max Value: {col_info['Max Value']}\n"
                #metadata_str += f"  Median Value: {col_info['Median Value']}\n"
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
        ) = compare_lists_matching(df_critique, df_ground_truth)
    except Exception as e:
        case_accuracy = 0
        print("".join(traceback.format_exc()))
        is_correct = False
        #print("YOU ARE NOT VERY GOOD AT THIS LOL")
        
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
    
    crit_info = (is_correct,is_correct_, case_accuracy_,cost.get('total_cost', 0.0),time_elapsed,score)
    
    return crit_info 

def precursor(length, id_, log_dir_, experiment_name,i_):
    # Initialize required variables
    case_path = f"{length}_{id_}"
    is_correct = False
    is_correct_ = False
    case_accuracy_ = 0
    score = 0
    case_accuracy = 0
    cost_summary = []
    start_time = time.time()
    token_tracker = TokenUsageTracker()
    script = ""
    op_hist_ = ""
    hint_source = p.hint_source
    
        # decided through parameters
    len_id = length
    max_len_id = length
    target_id = id_  # [18,2,32,33,96,16,27,78,91,18]
    max_target_id = id_
    target_per = p.target_per
    is_perc = p.is_perc

    # Best Parameters: {'distinct_value_count': 0.8781174363909454, 'distinct_value_ratio': 0.027387593197926163, 'emptiness': 0.6704675101784022, 'fd': 0.41730480236712697, 'leftness_group_by': 0.5586898284457517, 'leftness_join': 0.14038693859523377, 'peak_frequency': 0.1981014890848788, 'sortedness': 0.8007445686755367, 'source_samples': 0.9682615757193975, 'target_samples': 0.31342417815924284, 'value_overlap_jc': 0.6923226156693141, 'value_overlap_js': 0.8763891522960383, 'value_range_overlap': 0.8946066635038473}

    # Updated Parameters

    anon_flag = p.anon_flag

    # join_hints = [distinct_value_ratio, jaccard_similarity, jaccard_condition, value_range_overlap, leftness, sortedness]
    # aggregate_hints = [distinct_value_ratio, leftness, emptiness, peak_frequency]
    target_length = p.target_length 
    source_length = p.source_length

    join_flag = p.join_flag
    aggregate_flag = p.aggregate_flag

#3
# join_hints = [dvr, js, jc, vro, leftness, sortedness]
    join_hints_truncate = p.join_hints_truncate

    # join_hints_truncate = [
    #     0.5,#0.1981014890848788,  # distinct_value_ratio (dvr)
    #     0.6918771139504734,  # value_overlap_js (js)
    #     0.5331652849730171,  # value_overlap_jc (jc)
    #     0.6865009276815837,  # value_range_overlap (vro)
    #     0.5,#0.03905478323288236, # leftness_join (leftness)
    #     0.5#0.0983468338330501   # sortedness
    # ]

    aggregate_hints_truncate = p.aggregate_hints_truncate


    fd_flag = p.fd_flag
    token_limit = p.token_limit
    model = p.model
    path_to_files = f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/"
    # Counting files starting with 'test' in this subfolder
    file_count = sum(
        1
        for _, _, files in os.walk(path_to_files)
        for file in files
        if file.startswith("test")
    )
    
    #print(file_count)

    if file_count > 1:
        json_file_path = "data/chatgpt_github_ms.json"
    else:            
        json_file_path = "data/chatgpt_github_ss.json"

    # log_dir = "logs-auto-suggest-llm-proof-bayesian"
    log_dir = log_dir_
    main_folder = "autopipeline-benchmarks/github-pipelines"

    allowed_operation_list = [
        "JOIN",
        "UNION",
        "GROUP_BY/AGGREGATE",
        "PIVOT",
        "UNPIVOT",
        "NO_MORE_OPERATION",
    ]

    task_list = get_test_cases_ids(
        json_file_path, len_id, max_len_id, target_id, max_target_id
    )

    logger = create_logger("AUTOSUGGEST", log_dir, len_id, target_id, max_target_id)

    q_count = {"total": 0, "in_task": 0}

    # language = 'sql' #or 'python'

    ################## Run for each task ##################

    for task in task_list:

        q_count["in_task"] = 0

        logger.info("Started Experiment for : " + str(task))

        cost_summary = []

        start_time = time.time()
        token_tracker = TokenUsageTracker()
        cost_summary.append(token_tracker.cost_summary())
        # #print(cost_summary)

        len_idx_target_idx = task[6:]

        # #print(len_idx_target_idx)

        # Get the information of the target and source data

        (
            target_data_name,
            target_data_schema,
            target_samples,
            file_count,
            source_data_name_list,
            source_data_schema_list,
            source_samples_list,
        ) = get_test_info(json_file_path, len_idx_target_idx, main_folder, anon_flag)
        # added anon_flag to get_test_info() call

        # 0 to ask for operator and 1 for column and 2 to generate script
        toggle_operator = 0
        history_op = []
        history_elements = []
        operation_history = []

        llm_client = LLMClient(model=model, tracker=token_tracker, logger=logger)
        break_flag = 1

        while break_flag:

            prompt = get_prompt(prompt_type="get_next_operator", max_tokens = token_limit,model=model,allowed_operation_list=allowed_operation_list,
                            operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema,
                            target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                            directory = main_folder, len_idx_target_idx = len_idx_target_idx,
                            target_perc = target_per, is_perc = is_perc, target_length = target_length, source_length = source_length, hint_source = hint_source)
            if(prompt[0] == '-1') : 
                    logger.info("Token Limit Exceeded")
                    break_flag = 2
                    break
            # print(prompt)
            # # sys.exit()
            res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Ask For Operator")
            operation = get_operation(res[0])

            # sys.exit()
            # operation = 'JOIN'
            
            if operation == 'JOIN' :
                    # get join prompt 
                    prompt = get_prompt(prompt_type="join", max_tokens = token_limit,model=model,allowed_operation_list=allowed_operation_list,
                    operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema,
                    target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                    directory = main_folder, len_idx_target_idx = len_idx_target_idx, 
                    target_perc = target_per, is_perc = is_perc, target_length = target_length,join_flag = join_flag, join_hints_truncate = join_hints_truncate, hint_source = hint_source)
                    # sys.exit()
                    if(prompt[0] == '-1') : 
                            logger.info("Token Limit Exceeded")
                            break_flag = 2
                            break

                    # print(prompt[0])
                    # sys.exit()

                    res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Configure Join")
                    joined_columns = get_columns_join(res[0])
                    history_elements.append(joined_columns)
                    operation_history.append(operation + ' : ' + str(joined_columns))

                    # run llm and get join columns 
                    # add it to the history
                    pass 
            elif operation == 'GROUP_BY/AGGREGATE' :
                    # get group by prompt 
                    prompt = get_prompt(prompt_type="group_by_aggregate", max_tokens = token_limit,model=model,allowed_operation_list=allowed_operation_list,
                    operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema,
                    target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                    directory = main_folder, len_idx_target_idx = len_idx_target_idx, 
                    target_perc = target_per, is_perc = is_perc, target_length = target_length, aggregate_flag = aggregate_flag, aggregate_hints_truncate = aggregate_hints_truncate, hint_source = hint_source)
                    # sys.exit()
                    if(prompt[0] == '-1') : 
                            logger.info("Token Limit Exceeded")
                            break_flag = 2
                            break

                    # run llm and get group by column
                    # print(prompt[0]) 
                    # sys.exit()
                    res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Configure Group by/Aggergate")
                    # print(res[0])
                    # add it to the history
                    group_by_column = re.sub(r'```json\n|\n|```', '', res[0])
                    history_elements.append(res)
                    operation_history.append(group_by_column)
                    #operation_history.append(operation + ' : [ group_by : {group_by_column[0]}, aggregate : {group_by_column[1]}, aggregation_function : {group_by_column[2]} ]'.format(group_by_column = group_by_column))
                    pass
            elif operation == 'UNION' :
                    prompt = get_prompt(prompt_type="union", max_tokens = token_limit,model=model,allowed_operation_list=allowed_operation_list,
                    operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema,
                    target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                    directory = main_folder, len_idx_target_idx = len_idx_target_idx, 
                    target_perc = target_per, is_perc = is_perc, target_length = target_length,hint_source = hint_source)

                    if(prompt[0] == '-1') : 
                            logger.info("Token Limit Exceeded")
                            break_flag = 2
                            break

                    res = query_gpt(llm_client,model,prompt, q_count,logger, cost_summary, token_tracker, type = "Configure Union")
                    # print(res[0])
                    tables_ = get_columns(res[0])
                    history_elements.append(tables_)
                    operation_history.append(operation + ' : ' + str(tables_))
                    pass
            elif operation == 'PIVOT' :
                    operation_history.append(operation)
                    pass 
            elif operation == 'UNPIVOT' :
                    operation_history.append(operation)
                    pass
            elif operation == 'NO_MORE_OPERATION' :
                    # generate python script 
                    # do similarity search 
                    # go to next 
                    break_flag = 0 
                    pass
            else :
                    pass

        #print(operation_history)

        if break_flag == 0:
            # Generate Table and Compare
            # ss = get_source_with_location(file_count, source_data_name_list,source_data_schema_list, source_samples_list, main_folder, len_idx_target_idx)
            target_file_location = "{main_folder}/length{len_idx_target_idx}/target_multisource.csv".format(
                main_folder=main_folder, len_idx_target_idx=len_idx_target_idx
            )
            ground_truth_location = (
                "{main_folder}/length{len_idx_target_idx}/target.csv".format(
                    main_folder=main_folder, len_idx_target_idx=len_idx_target_idx
                )
            )
            Path(target_file_location).touch()
            # put this in a loop
            script_cnt = 0
            error_str = ""
            while script_cnt < 5:
                prompt = get_prompt(prompt_type="python_script", max_tokens = token_limit,model=model,allowed_operation_list=allowed_operation_list,
                            operation_history = operation_history,target_data_name = target_data_name,target_data_schema = target_data_schema, 
                            target_samples = target_samples,file_count = file_count,source_data_name_list = source_data_name_list,source_data_schema_list = source_data_schema_list, 
                            directory = main_folder, len_idx_target_idx = len_idx_target_idx, 
                            target_perc = target_per, is_perc = is_perc, target_length = target_length, error_string = error_str,target_file_location = target_file_location, hint_source = hint_source)


                if prompt[0] == "-1":
                    logger.info("Token Limit Exceeded")
                    break_flag = 2
                    break

                res = query_gpt(
                    llm_client,
                    model,
                    prompt,
                    q_count,
                    logger,
                    cost_summary,
                    token_tracker,
                    type="Get Python Script",
                )
                script = res[0].split("```Python")[1].split("```")[0].strip()
                # #print(script)
                response = execute_python(script)
                #print(response)
                error_str = error_str + response + "\n"
                # #print(error_str)
                if response == "Success":
                    break
                script_cnt += 1

            if response == "Success":
                # save file here 
                # file_name
                if not os.path.exists(f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/script_archive"):
                    os.makedirs(f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/script_archive")
                with open(
                    f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/script_archive/{experiment_name}_{i_}.py",
                    "w",
                ) as file:
                    file.write(script)

                try : 
                # name_of_experiment_pass_1
                    df_our_response = pd.read_csv(
                        target_file_location, low_memory=False
                    )
                    df_ground_truth = pd.read_csv(
                        ground_truth_location, low_memory=False
                    )
                    df_ground_truth.drop(
                        columns=df_ground_truth.columns[0], axis=1, inplace=True
                    )
                    (
                        case_accuracy_,
                        is_correct_,
                        similarity_scores_
                    ) = compare_lists_matching_soft(df_our_response, df_ground_truth)
                    eps = 0.1
                    if case_accuracy_ < eps:
                        case_accuracy_ = 0
                    try:
                        (
                            case_accuracy,
                            is_correct,
                            similarity_scores,
                            validation_error,
                        ) = compare_lists_matching(df_our_response, df_ground_truth)
                        '''
                        print(
                            case_accuracy, is_correct, similarity_scores, validation_error
                        )
                        '''
                    except Exception as e:
                        print("".join(traceback.format_exc()))
                        is_correct = False
                    # calculate score 
                    score = calculate_score(df_ground_truth, df_our_response)
                    # print(
                    #     case_accuracy, is_correct, is_correct_,similarity_scores, validation_error
                    # )
                    # logger.info(
                    #     "Task : "
                    #     + task
                    #     + " Case Accuracy : "
                    #     + str(case_accuracy)
                    #     + ", is_correct : "
                    #     + str(is_correct)
                    #     + ", similarity_score : "
                    #     + str(similarity_scores)
                    # )
                except Exception as e:
                    print("".join(traceback.format_exc()))
                    case_accuracy = 0
                    is_correct = False
                    is_correct_ = False
                    case_accuracy_ = 0
                    score = 0
        op_hist_ = str(operation_history)
        end_time = time.time()

    # Only try to write the file if script was actually generated
    if script:
        with open(
            f"autopipeline-benchmarks/github-pipelines/length{length}_{id_}/python_recovered.py",
            "w",
        ) as file:
            file.write(script)
    case_path = f"{length}_{id_}"
    cost_data = token_tracker.cost_summary()  # This returns a dictionary
    total_cost = cost_data.get('total_cost', 0.0)  # Safely get total_cost with default
    time_elapsed = end_time - start_time
    #print("++++++++++++++++++++++++++++++++++++")
    #print(cost_data)
    #print("++++++++++++++++++++++++++++++++++++")
    ms_info = (
        is_correct,
        is_correct_,
        case_accuracy_,
        total_cost,  # Use the extracted total_cost value
        time_elapsed,
        score, 
        op_hist_
    )
    print(f"ms_info: {ms_info}")
    logger.info("Total Queries Made : {q}".format(q=q_count["total"]))
    return ms_info
        
    # except Exception as e:
    #     print("".join(traceback.format_exc()))
    #     end_time = time.time()
    #     time_elapsed = end_time - start_time
    #     ms_info = (
    #         False,
    #         False,
    #         0.0,  # Default cost when there's an error
    #         total_cost,
    #         time_elapsed,
    #         0.0,
    #         op_hist_
    #     )
    #     return ms_info

def avg_tup(list_tup):
    avg_cost = 0
    avg_lat = 0
    for tup in list_tup:
        avg_cost += tup[3]
        avg_lat += tup[4]
    avg_cost = avg_cost/len(list_tup)
    avg_lat = avg_lat/len(list_tup)
    
    avg = (list_tup[0][0], avg_cost, avg_lat)
    return avg

def avg_tup_(list_tup):
    print("_________________________")
    print(f"averaging {list_tup}")
    avg_cost = 0
    avg_lat = 0
    avg_score = 0
    for tup in list_tup:
        avg_cost += tup[3]
        avg_lat += tup[4]
        avg_score += tup[2]
    avg_cost = avg_cost/len(list_tup)
    avg_lat = avg_lat/len(list_tup)
    avg_score = avg_score/len(list_tup)
    #here
    avg = (list_tup[0][1], avg_score,avg_cost, avg_lat)
    return avg

def ms(length, id, log_dir,experiment_name):
    results = [] 
    true_tup = []
    false_tup = []
    true_tup_ = []
    false_tup_ = []
    for i in range(0,p.no_of_runs):
        try:
            ms_info = precursor(length, id, log_dir,experiment_name,i)
        except Exception as e:
            print("".join(traceback.format_exc()))
            ms_info = ("precursor error " + str(e))
        #print(ms_info)
        results.append(ms_info)
    
    for tup in results:
        Autologtuple((f"{length}_{id}",) + tup,
                     sheet_dir["sheet_2"],
                     worksheet_name=sheets["sm"],
                     creds_file=creds_path
                    )
        if tup[1] == True:
            true_tup_.append(tup)
            #print(f"{tup} in true tup")
        else:
            #print(f"{tup} in false tup")
            false_tup_.append(tup)
            
        if tup[0] == True:
            true_tup.append(tup)
            #print(f"{tup} in true tup")
        else:
            #print(f"{tup} in false tup")
            false_tup.append(tup)
    
    
    if len(true_tup_) >= p.majority_voting:
        print(f"avging {true_tup_}")
        avged_tup_ = avg_tup_(true_tup_)
    else: 
        print(f"avging {false_tup_}")
        avged_tup_ = avg_tup_(false_tup_)
        
    if len(true_tup) >= p.majority_voting:
        avged_tup = avg_tup(true_tup)
    else:
        avged_tup = avg_tup(false_tup)     
    #
    return avged_tup + avged_tup_

def crit(length, id_, experiment_name):
    a_results = []
    ab_results = []
    abc_results = []
    
    #for strict match
    a_true = []
    a_false = []
    ab_true = []
    ab_false = []
    abc_true = []
    abc_false = []
    
    #for soft match
    a_true_ = []
    a_false_ = []
    ab_true_ = []
    ab_false_ = []
    abc_true_ = []
    abc_false_ = []
    
    for i in range(0,p.no_of_runs):
        # def critique(length, id_, nature, log_dir_, flags, is_def, i_, experiment_name):
        abl_a = critique(length, id_, "og_query.txt", f"crit_logs/{length}_{id_}/", [1,0,0],0,i, experiment_name)
        
        abl_ab = critique(length, id_, "query.txt", f"crit_logs/{length}_{id_}/", [1,1,0],1,i, experiment_name)
        
        abl_abc = critique(length, id_, "query.txt", f"crit_logs/{length}_{id_}/", [1,1,1],1,i, experiment_name)

        a_results.append(abl_a)
        ab_results.append(abl_ab)
        abc_results.append(abl_abc)
    
    for tup in a_results:
        Autologtuple((f"{length}_{id_}",) + tup,
                     sheet_dir["sheet_2"],
                     worksheet_name=sheets["sc"],
                     creds_file=creds_path
                    )
        if tup[1] == True:
            a_true_.append(tup)
        else:
            a_false_.append(tup)
        if tup[0] == True:
            a_true.append(tup)
        else:
            a_false.append(tup)
    for tup in ab_results:
        Autologtuple((f"{length}_{id_}",) + tup,
                     sheet_dir["sheet_2"],
                     worksheet_name=sheets["sc"],
                     creds_file=creds_path
                    )
        if tup[1] == True:
            ab_true_.append(tup)
        else:
            ab_false_.append(tup)
        if tup[0] == True:
            ab_true.append(tup)
        else:
            ab_false.append(tup)
    for tup in abc_results:
        Autologtuple((f"{length}_{id_}",) + tup,
                     sheet_dir["sheet_2"],
                     worksheet_name=sheets["sc"],
                     creds_file=creds_path
                    )
        if tup[1] == True:
            abc_true_.append(tup)
        else:
            abc_false_.append(tup)
        if tup[0] == True:
            abc_true.append(tup)
        else:
            abc_false.append(tup)
    
    if len(a_true) >= p.majority_voting:
        avg_a  = avg_tup(a_true)
    else:
        avg_a = avg_tup(a_false)
    if len(a_true_) >= p.majority_voting:
        avg_a_ = avg_tup_(a_true_)
    else:
        avg_a_ = avg_tup_(a_false_)
    
    if len(ab_true) >= p.majority_voting:
        avg_ab  = avg_tup(ab_true)
    else:
        avg_ab = avg_tup(ab_false)
    if len(ab_true_) >= p.majority_voting:
        avg_ab_ = avg_tup_(ab_true_)
    else:
        avg_ab_ = avg_tup_(ab_false_)
        
    if len(abc_true) >= p.majority_voting:
        avg_abc  = avg_tup(abc_true)
    else:
        avg_abc = avg_tup(abc_false)
    if len(abc_true_) >= p.majority_voting:
        avg_abc_ = avg_tup_(abc_true_)
    else:
        avg_abc_ = avg_tup_(abc_false_)
    
    
    avg_results = [avg_a + avg_a_, avg_ab + avg_ab_, avg_abc + avg_abc_]
    print("CRITIQUE FINAL RESULTS:")
    print(avg_results)
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    max_val = -1
    max_ind = 0
    i = 0
    
    for i, result in enumerate(avg_results):
        if result[4] > max_val:
            max_val = result[4]
            max_ind = i
            
    avg_results[max_ind] += ('MAX',)
    return avg_results


def main():
    length = p.len_id
    start = p.target_id
    end = p.max_target_id
    Autologtuple(("Start", "Test:", f"{length}_{start}",f"{length}_{end}",),sheet_dir["sheet_1"],
                creds_file=creds_path )

    cases = list(range(start,end))

    experiment_name = p.experiment_name
    

    # lengths = ["length5_0",  "length5_3",  "length5_10", "length5_34"]
    # lengths = ["length5_36", "length5_39", "length5_40", "length5_64"]
    # lengths = ["length5_69", "length5_70", "length5_75", "length5_87"]
    # lengths = ["length5_89", "length5_92", "length5_98", "length5_99"]
    lengths = ["length5_10"]



    # Get the path to credentials.json relative to the autologger package
    
    for leng in lengths:
        length = int(leng[6])
        case = int(leng[8:])
        case_path = f"{length}_{case}"
        log_dir = f"crit_logs/{case_path}"

    # for case in cases : 

    #     case_path = f"{length}_{case}"
    #     log_dir = f"crit_logs/{case_path}"
      
        try:
            #compute multisource
            ms_info = ms(length, case, log_dir, experiment_name)
            
            # Format as a single row with consistent columns
            #print(f"case_path: {case_path} + ms_info: {ms_info}")
            result = (case_path,) + ms_info 
            
            Autologtuple(
                result,
                sheet_dir["sheet_1"],
                worksheet_name=sheets["am"],
                creds_file=creds_path
            )
            
            # critique iff ms is wrong
            if not result[1]:
                crit_info = crit(length, case, experiment_name)

                for crit_ in crit_info:
                    Autologtuple(
                        (case_path, ) + crit_ ,
                        sheet_dir["sheet_1"],
                        worksheet_name=sheets["ac"],
                        creds_file=creds_path
                    )
            
        except Exception as e:
            print("".join(traceback.format_exc()))
            print(f"Error processing case {case_path}: {str(e)}")

if __name__ == "__main__":
    main()
