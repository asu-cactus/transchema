import time
import os
import pandas as pd
import re
import traceback
import pdb

from auto_suggest_llm_util import get_filtered_functional_dependency, calculate_score
from util.utils import execute_python, get_test_info
from llm.llm_models import TokenUsageTracker, LLMClient
from validation.hard_match import compare_lists_matching, compare_tables_matching
from validation.soft_match import compare_lists_matching_soft
from log_util.log_util import create_logger


def critique(args, length, id_, log_dir_, flags, is_def, operation_history):
    log_dir = log_dir_
    validate_fn = compare_tables_matching if getattr(args, "validation", "hard_match") == "autopipeline" else compare_lists_matching

    # Benchmark selector: github | monteprep
    benchmark = getattr(args, "benchmark", "github")
    main_folder = "autopipeline-benchmarks/monteprep-pipelines" if benchmark == "monteprep" else "autopipeline-benchmarks/github-pipelines"
    path_to_files = f"{main_folder}/length{length}_{id_}/"
    # Counting files starting with 'test' in this subfolder
    file_count = sum(
        1
        for _, _, files in os.walk(path_to_files)
        for file in files
        if file.startswith("test")
    )

    len_id = length
    target_id = id_
    max_target_id = id_
    len_idx_target_idx = str(len_id) + "_" + str(target_id)

    token_tracker = TokenUsageTracker()

    start_time = time.time()

    if is_def == 1:
        type_ = "DEF_CRITIQUE"
    else:
        type_ = "NEW_CRITIQUE"
    logger = create_logger(type_, log_dir, len_id, target_id, max_target_id)

    llm_client = LLMClient(model=args.model, tracker=token_tracker, logger=logger)

    # #print(res[0])
    with open(
        main_folder + "/length" + len_idx_target_idx + "/python_recovered.py", mode="r"
    ) as f:
        python_code = f.read()
    # target_location_critique = (
    #     main_folder
    #     + "/length"
    #     + len_idx_target_idx
    #     + "/target_multisource_critique_"
    #     + args.critique_type
    #     + ".csv"
    # )
    query_generator = f"""
The following is the operation history of a data transformation pipeline which produce the incorrect output: {operation_history}.
Check if the last operation involves a groupby/aggregation operation, and if so, generate a python code to aggregate using all other aggregation functions.
We consider five aggregation functions: sum, mean, count, max, and min. 
You should generate a python code that applies these aggregation functions to the last operation in the operation history.
You can skip the operation that is in the current operation history, so you will run the rest of the five aggregation functions.
If the last operation in the operation history is not aggregation, just reply "NOT GROUPBY/AGGREGATION" without any further explanation.
For each aggregation function, write the final output of the python code to {main_folder}/length{len_idx_target_idx}/target_critique_$aggregation_function$.csv
Replace the $aggregation_function$ with the name of the aggregation function.
Note:
- Make sure to write the python code in-between "```Python" and "```"
- Please keep the final output columns the same as it was in the python script given. [Strictly do not add prefix or suffix to the column names]
- Do not use assignment operation for any column.
Previous Python Code : ```Python 
{python_code}
```
    """

    res_gen = llm_client.gpt(query_generator)[0]
    if res_gen.strip() == "NOT GROUPBY/AGGREGATION":
        logger.info("The last operation is not a groupby/aggregation operation.")
        return (False, False, 0.0, 0.0, 0.0, 0.0)

    pattern = re.compile(r"```Python(.*?)```", re.DOTALL | re.IGNORECASE)
    match = pattern.search(res_gen)
    script = match.group(1).strip()

    logger.info(query_generator)
    logger.info(res_gen)
    logger.info(token_tracker.cost_summary())
    cost = token_tracker.cost_summary()
    end_time = time.time()
    time_elapsed = end_time - start_time
    ##print(script)
    response = execute_python(script)
    logger.info(response)

    ground_truth_location = f"{main_folder}/length{len_idx_target_idx}/target.csv"

    df_ground_truth = pd.read_csv(ground_truth_location, low_memory=False)
    df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)

    target_critique_locations = []
    # Iterate through {main_folder}/length{len_idx_target_idx}/, get csv files that start with 'target_critique_'
    for file in os.listdir(f"{main_folder}/length{len_idx_target_idx}/"):
        if file.startswith("target_critique_") and file.endswith(".csv"):
            target_critique_locations.append(
                f"{main_folder}/length{len_idx_target_idx}/{file}"
            )

    is_correct = False
    best_is_correct_soft = False
    best_case_accuracy_soft = 0
    best_score = 0
    for target_critique_location in target_critique_locations:
        try:
            df_critique = pd.read_csv(target_critique_location, low_memory=False)
            (
                case_accuracy,
                is_correct,
                similarity_scores,
                validation_error,
            ) = validate_fn(df_ground_truth, df_critique)
            # need to change the definition, the sequence in the definition is incorrect
            (
                case_accuracy_soft,
                is_correct_soft,
                similarity_scores_soft,
            ) = compare_lists_matching_soft(df_critique, df_ground_truth)
            ##print("ACCURATCY CBELOW ")
            eps = 0.1
            if case_accuracy_soft < eps:
                case_accuracy_soft = 0
            # print(f"{case_accuracy}, {is_correct}")

            logger.info(is_correct)

            if is_correct:
                break

            score = calculate_score(df_ground_truth, df_critique)

            if best_case_accuracy_soft < case_accuracy_soft:
                best_case_accuracy_soft = case_accuracy_soft
                best_is_correct_soft = is_correct_soft
                best_score = score

        except Exception as e:
            continue
            # print("YOU ARE NOT VERY GOOD AT THIS LOL")

    if not is_correct:
        case_accuracy_soft = best_case_accuracy_soft
        is_correct_soft = best_is_correct_soft
        score = best_score
    crit_info = (
        is_correct,
        is_correct_soft,
        case_accuracy_soft,
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

    if args.intermediate_materialization_flag:
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
