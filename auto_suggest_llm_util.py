import os
import time
import re
from pathlib import Path
from dataclasses import dataclass
import pdb
import pandas as pd
import logging
from datetime import datetime
from util.utils import get_test_info
from test_scope import get_test_cases_ids
from hints.hint import get_hints
import auto_suggest_llm_prompts as prt
import tiktoken
from quality.quality import analyze_functional_dependencies
from valentine import valentine_match, algorithms

# import prompts 
from prompts.next_operator_prompt import get_next_operator_prompt
from prompts.next_operator_prompt import get_next_operator_prompt
from prompts.configuration_prompts import get_join_prompt, get_group_by_aggregate_prompt, get_union_prompt
from prompts.code_generation_prompt import get_python_script,get_python_script_with_intermediate_materialization
from prompts.next_operator_prompt_with_intermediate_materialization import (
    get_next_operator_prompt_with_intermediate_materialization
)

def get_prompt(
    prompt_type,
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    directory,
    len_idx_target_idx,
    source_data_name_list,
    source_data_schema_list,
    error_string="",
    max_tokens=128000,
    target_perc=10,
    is_perc=True,
    target_length=3,
    source_length=3,
    join_flag=0,
    aggregate_flag=0,
    join_hints_truncate=[],
    aggregate_hints_truncate=[],
    fd_flag=0,
    model="gpt-4-turbo",
    hint_source="v1",
    save_path="",
    nth_intermediate_step=0,
    combine_ask_and_configure=False,
    no_thinking=False,
):
    """
    Args:
        save_path (str): Path to save the intermediate results.
        nth_intermediate_step (int): Current step at which to materialize the intermediate result.
            Show the intermediate results in the steps [1,2,3,...,n-1].
            Default is 0, which means no intermediate materialization.
        combine_ask_and_configure (bool): Whether try to combine the ask and configure steps.
        no_thinking (bool): Whether to disable the thinking process.
    """
    # we can generate hints here itself
    # we need these information
    # file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx

    # 2 types of tokens
    # static : content in the prompt without target examples
    # dynamic : target_examples
    # max_tokens = 128000 # for gpt4turbo

    if model == "gpt-4.1-mini":
        # According to https://github.com/openai/tiktoken/issues/395
        encoding = tiktoken.get_encoding("o200k_base")
    else:
        encoding = tiktoken.encoding_for_model(model)

    if nth_intermediate_step == 1:
        all_intermediate_results = []
    if nth_intermediate_step > 1:
        # Get the intermediate results only if nth_intermediate_step > 1 because at the 1st step won't
        # have intermediate results
        intermediate_dir = f"{directory}/length{len_idx_target_idx}/"
        all_intermediate_results = get_all_intermediate(
            intermediate_dir, encoding, source_length, nth_intermediate_step
        )

    source_information = get_source(
        file_count,
        source_data_name_list,
        source_data_schema_list,
        directory,
        len_idx_target_idx,
        source_length,
        encoding,
    )

    fd_hints = ""
    if fd_flag == 1:
        # calculate filtered functional dependency hints
        target_file_location = f"{directory}/length{len_idx_target_idx}/target.csv"
        df = pd.read_csv(target_file_location, low_memory=False)
        df = df.drop(df.columns[0], axis=1)
        keys, fds = get_filtered_functional_dependency(df)
        fd_hints = get_fd_hints(keys, fds)

        if nth_intermediate_step > 1:
            for step in range(1, nth_intermediate_step):

                file_path = f"{intermediate_dir}/intermediate_step{step}.csv"
                intermediate_df = pd.read_csv(file_path, low_memory=False)
                # Get functional dependency hints
                intermediate_keys, intermediate_fds = (
                    get_filtered_functional_dependency(intermediate_df)
                )
                intermediate_fd_hints = get_fd_hints_for_materialization(
                    intermediate_keys, intermediate_fds, step
                )
                fd_hints += intermediate_fd_hints

            # Get key column hints
            fd_hints += "\n\nKey column hints:\n"
            fd_hints += get_key_column_hints(keys, 0)
            for step in range(1, nth_intermediate_step):
                fd_hints += get_key_column_hints(intermediate_keys, step)

            # Get column matching hints
            fd_hints += "\n\nColumn Matching Hints:\n"
            for step in range(1, nth_intermediate_step):
                fd_hints += get_column_matching_hints(intermediate_df, df, step)

    if prompt_type == "get_next_operator":
        hints = get_hints(
            "get_next_operator",
            hint_source,
            target_data_schema,
            file_count,
            source_data_name_list,
            source_data_schema_list,
            directory,
            len_idx_target_idx,
            0,
            [],
        )
        static_prompt =  get_next_operator_prompt(
            allowed_operation_list,
            operation_history,
            target_data_name,
            target_data_schema,
            "",
            file_count,
            source_information,
            fd_hints,
            hints,
        )[0]
        static_prompt_length = len(encoding.encode(static_prompt))
        target_samples = get_target_samples(
            directory,
            len_idx_target_idx,
            target_perc,
            is_perc,
            target_length,
            max_tokens,
            static_prompt_length,
            encoding,
        )[0]

        if nth_intermediate_step > 0:
            prompt =  get_next_operator_prompt_with_intermediate_materialization(
                allowed_operation_list,
                operation_history,
                target_data_name,
                target_data_schema,
                target_samples,
                file_count,
                source_information,
                fd_hints,
                hints,
                all_intermediate_results,
                combine_ask_and_configure=combine_ask_and_configure,
                no_thinking=no_thinking,
            )[0]
        else:
            prompt =  get_next_operator_prompt(
                allowed_operation_list,
                operation_history,
                target_data_name,
                target_data_schema,
                target_samples,
                file_count,
                source_information,
                fd_hints,
                hints,
            )[0]

        # print(prompt,static_prompt_length)
        # print(static_prompt_length)
        # print(str(len(encoding.encode(str(target_samples)))))
        # print(str(len(encoding.encode(prompt))))

    elif prompt_type == "join":
        hints = get_hints(
            "join",
            hint_source,
            target_data_schema,
            file_count,
            source_data_name_list,
            source_data_schema_list,
            directory,
            len_idx_target_idx,
            join_flag,
            join_hints_truncate,
        )
        static_prompt =  get_join_prompt(
            allowed_operation_list,
            operation_history,
            target_data_name,
            target_data_schema,
            "",
            file_count,
            source_information,
            hints,
            fd_hints,
        )[0]
        static_prompt_length = len(encoding.encode(static_prompt))
        target_samples = get_target_samples(
            directory,
            len_idx_target_idx,
            target_perc,
            is_perc,
            target_length,
            max_tokens,
            static_prompt_length,
            encoding,
        )[0]
        prompt =  get_join_prompt(
            allowed_operation_list,
            operation_history,
            target_data_name,
            target_data_schema,
            target_samples,
            file_count,
            source_information,
            hints,
            fd_hints,
        )[0]

    elif prompt_type == "group_by_aggregate":
        hints = get_hints(
            "group_by_aggregate",
            hint_source,
            target_data_schema,
            file_count,
            source_data_name_list,
            source_data_schema_list,
            directory,
            len_idx_target_idx,
            aggregate_flag,
            aggregate_hints_truncate,
        )
        static_prompt =  get_group_by_aggregate_prompt(
            allowed_operation_list,
            operation_history,
            target_data_name,
            target_data_schema,
            "",
            file_count,
            source_information,
            hints,
            fd_hints,
        )[0]
        static_prompt_length = len(encoding.encode(static_prompt))
        target_samples = get_target_samples(
            directory,
            len_idx_target_idx,
            target_perc,
            is_perc,
            target_length,
            max_tokens,
            static_prompt_length,
            encoding,
        )[0]
        prompt =  get_group_by_aggregate_prompt(
            allowed_operation_list,
            operation_history,
            target_data_name,
            target_data_schema,
            target_samples,
            file_count,
            source_information,
            hints,
            fd_hints,
        )[0]

    elif prompt_type == "union":
        static_prompt =  get_union_prompt(
            allowed_operation_list,
            operation_history,
            target_data_name,
            target_data_schema,
            "",
            file_count,
            source_information,
        )[0]
        static_prompt_length = len(encoding.encode(static_prompt))
        target_samples = get_target_samples(
            directory,
            len_idx_target_idx,
            target_perc,
            is_perc,
            target_length,
            max_tokens,
            static_prompt_length,
            encoding,
        )[0]
        prompt =  get_union_prompt(
            allowed_operation_list,
            operation_history,
            target_data_name,
            target_data_schema,
            target_samples,
            file_count,
            source_information,
        )[0]

    elif prompt_type == "python_script":

        source_information_with_location = get_source_with_location(
            file_count,
            source_data_name_list,
            source_data_schema_list,
            source_length,
            directory,
            len_idx_target_idx,
            encoding,
        )
        # target_file_location = directory + '/length' + len_idx_target_idx + '/target_multisource.csv'
        # print(error_string)
        static_prompt =  get_python_script(
            allowed_operation_list,
            operation_history,
            target_data_name,
            target_data_schema,
            "",
            file_count,
            source_information_with_location,
            save_path,
            error_string,
        )[0]
        static_prompt_length = len(encoding.encode(static_prompt))
        target_samples = get_target_samples(
            directory,
            len_idx_target_idx,
            target_perc,
            is_perc,
            target_length,
            max_tokens,
            static_prompt_length,
            encoding,
        )[0]
        if nth_intermediate_step > 0:
            prompt =  get_python_script_with_intermediate_materialization(
                allowed_operation_list,
                operation_history,
                target_data_name,
                target_data_schema,
                target_samples,
                file_count,
                source_information_with_location,
                save_path,
                error_string,
                all_intermediate_results,
            )[0]
        else:
            prompt =  get_python_script(
                allowed_operation_list,
                operation_history,
                target_data_name,
                target_data_schema,
                target_samples,
                file_count,
                source_information_with_location,
                save_path,
                error_string,
            )[0]
    else:
        raise ValueError(f"Invalid prompt type {prompt_type}.")

    # print(prompt)
    # print(len(encoding.encode(prompt)))
    prompt_len = len(encoding.encode(prompt))
    if prompt_len > max_tokens:
        # return ["-1"]
        raise Exception(f"Prompt length {prompt_len} exceeds maximum tokens.")

    return prompt
    # return [prompt]
    # Static Dynamic tokens
    # Dynamic tokens


def get_target_string(df, rem_tokens, encoding):

    # string should be target rows in list
    examples_l = df.values.tolist()
    examples = str(examples_l)

    # if all passes do not check further
    if len(encoding.encode(examples)) < rem_tokens:
        return examples

    # if not then do binary search on exact number of examples that can be in there
    l = 0
    r = len(examples_l) - 1
    ans = 0
    while l < r:

        mid = (l + r) // 2

        # print(l,mid,r)

        # examples upto mid
        temp_l = examples_l[: mid + 1]
        # how much string is being used
        temp = str(temp_l)
        encode_len = len(encoding.encode(temp))

        # print(rem_tokens, encode_len)

        if encode_len <= rem_tokens:
            ans = mid
            l = mid + 1
        elif encode_len > rem_tokens:
            r = mid - 1

    # print('ans :', ans)
    temp_l = examples_l[:ans]
    # print(len(encoding.encode(str(temp_l))))
    return [str(temp_l)]


def get_target_samples(
    directory,
    len_idx_target_idx,
    target_perc,
    is_perc,
    target_length,
    max_tokens,
    static_prompt_length,
    encoding,
):
    # print(directory,len_idx_target_idx, target_perc,is_perc, target_length, max_tokens, static_prompt_length)
    target_csv_path = directory + "/length" + len_idx_target_idx + "/target.csv"
    target_df = pd.read_csv(target_csv_path, low_memory=False)
    target_df = target_df.drop(target_df.columns[0], axis=1)

    # sampling
    if is_perc:
        target_df_sampled = target_df.sample(frac=target_perc / 100, replace=False)
    else:
        target_df_sampled = target_df.sample(
            n=min(target_length, target_df.shape[0]), replace=False
        )
    # print(static_prompt_length, max_tokens - static_prompt_length)
    target_samples_string = get_target_string(
        target_df_sampled, max_tokens - static_prompt_length, encoding
    )  # -1000 buffer for good measures

    return [target_samples_string]


def get_source(
    file_count,
    source_data_name_list,
    source_data_schema_list,
    directory,
    len_idx_target_idx,
    sample_length,
    encoding,
):
    ss = "\n"
    for i in range(file_count):
        ss += "\tSource {i}:\n".format(i=i)
        ss += "\tSource {i} Name: {source_data_name_list}\n".format(
            i=i, source_data_name_list=source_data_name_list[i]
        )
        ss += "\tSource {i} Schema: {source_data_schema_list}\n".format(
            i=i, source_data_schema_list=source_data_schema_list[i]
        )
        source_samples = get_source_samples(
            directory, len_idx_target_idx, i, sample_length, encoding
        )
        ss += "\tSource {i} Examples: {source_samples_list}\n".format(
            i=i, source_samples_list=source_samples
        )
    return ss


def get_source_samples(directory, len_idx_target_idx, i, sample_length, encoding):
    # print(directory,len_idx_target_idx)
    filename = "{main_directory}/length{len_idx_target_idx}/test_{i}.csv".format(
        main_directory=directory, len_idx_target_idx=len_idx_target_idx, i=i
    )
    # print(filename)
    # sys.exit()
    source_df = pd.read_csv(filename, low_memory=False)
    source_df = source_df.drop(source_df.columns[0], axis=1)
    source_df_sampled = source_df.head(min(source_df.shape[0], sample_length))
    source_samples_string = get_target_string(
        source_df_sampled, 128000, encoding
    )  # -1000 buffer for good measures # for now no limit on max_tokens for source
    return source_samples_string


def get_source_with_location(
    file_count,
    source_data_name_list,
    source_data_schema_list,
    source_length,
    main_directory,
    len_idx_target_idx,
    encoding,
):
    ss = ""
    for i in range(file_count):
        ss += "\tSource {i}:\n".format(i=i)
        ss += "\tSource {i} Name: {source_data_name_list}\n".format(
            i=i, source_data_name_list=source_data_name_list[i]
        )
        ss += "\tSource {i} Schema: {source_data_schema_list}\n".format(
            i=i, source_data_schema_list=source_data_schema_list[i]
        )
        source_samples_list = get_source_samples(
            main_directory, len_idx_target_idx, i, source_length, encoding
        )
        ss += "\tSource {i} Examples: {source_samples_list}\n".format(
            i=i, source_samples_list=source_samples_list
        )
        ss += "\tSource {i} File Location: {main_directory}/length{len_idx_target_idx}/test_{i}.csv\n".format(
            i=i, main_directory=main_directory, len_idx_target_idx=len_idx_target_idx
        )
    return ss


@dataclass
class IntermediateResult:
    schema: list
    source_samples_string: str
    file_path: str


def get_all_intermediate(
    intermediate_dir, encoding, sample_length, nth_intermediate_step
):
    def get_intermediate(file_path, encoding, sample_length):
        source_df = pd.read_csv(file_path, low_memory=False)
        source_df_sampled = source_df.head(min(source_df.shape[0], sample_length))
        source_samples_string = get_target_string(
            source_df_sampled, 128000, encoding
        )  # -1000 buffer for good measures # for now no limit on max_tokens for source

        schema = source_df.columns.tolist()
        return IntermediateResult(schema, source_samples_string, str(file_path))

    # assert (
    #     nth_intermediate_step > 0
    # ), f"current_step should be greater than 1, otherwise no intermediate results are available, got {nth_intermediate_step}"
    if nth_intermediate_step == 1:
        return []

    source_dir = Path(intermediate_dir)
    # Find all files matching the pattern "test{integer}.csv" in the source directory
    all_intermediate_results = []
    for step in range(1, nth_intermediate_step):
        file_path = source_dir / f"intermediate_step{step}.csv"
        intermediate_result = get_intermediate(file_path, encoding, sample_length)
        all_intermediate_results.append(intermediate_result)

    return all_intermediate_results


def create_logger(
    type_, log_dir, pipeline_len_start_idx, target_start_idx, max_target_idx
):
    # Get current system time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the log file name with the current time
    log_file = (
        f"{pipeline_len_start_idx}_target{target_start_idx}_{type_}_{current_time}.log"
    )

    # Check if the log directory exists, create it if it does not
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Setup logging
    logging.basicConfig(
        filename=os.path.join(log_dir, log_file),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="a+",
    )
    return logging.getLogger()


def get_operation(s):
    match = re.search(r"\$(.*?)\$", s)
    if match:
        extracted_word = match.group(1)
        return extracted_word
    else:
        extracted_word = "No match found"


def get_columns(s):
    matches = re.findall(r"\$(.*?)\$", s)
    return matches


def get_columns_join(s):
    result = re.search(r"\$(.*?)\$", s)
    if result:
        extracted_content = result.group(1)
        return extracted_content

    return "No match found"


def get_columns_aggr(s):
    elements = s.strip("[]").split(",")

    # Remove the quotes and dollar signs from each element
    elements = [element.strip(" ") for element in elements]

    elements = [element.strip('"') for element in elements]

    elements = [element.strip("$") for element in elements]

    res = [elements[:-2], elements[-2], elements[-1]]

    return res

def cost_compare(cost1, cost2, model):
    cost = dict()
    cost["total_cost"] = cost2["total_cost"] - cost1["total_cost"]
    cost["detailed_cost"] = dict()
    if model in cost1["detailed_cost"].keys():
        cost["detailed_cost"][model] = {
            "completion_tokens": cost2["detailed_cost"][model]["completion_tokens"]
            - cost1["detailed_cost"][model]["completion_tokens"],
            "prompt_tokens": cost2["detailed_cost"][model]["prompt_tokens"]
            - cost1["detailed_cost"][model]["prompt_tokens"],
            "cost": cost2["detailed_cost"][model]["cost"]
            - cost1["detailed_cost"][model]["cost"],
        }
    else:
        cost["detailed_cost"][model] = cost2["detailed_cost"][model]

    # print('calculated Cost : ', cost)

    return cost


def increment_count(q):
    q["total"] += 1
    q["in_task"] += 1
    return


# llm_client,model,prompt, q_count, cost_summary, token_tracker, type = "Ask For Operator"
def query_gpt(
    llm_model, model, prompt, q_count, logger, cost_summary, token_tracker, type
):
    start_time = time.time()
    logger.info("Query of Type : {type_}".format(type_=type))
    # run the prompt and get the result
    res = llm_model.gpt(prompt)
    # log the prompt
    logger.info("Prompt to ask for operator : {prompt}".format(prompt=prompt))
    # log the result
    logger.info("Result Recieved :  {res}".format(res=res[0]))
    end_time = time.time()
    # calculate append incremental cost in cost_summary, the last one will be the total task cost
    cost_summary.append(token_tracker.cost_summary())

    # calculate cost associated with this task
    cost = cost_compare(cost_summary[-2], cost_summary[-1], model)
    # print('Cost : ', cost)

    # log that cost
    logger.info("Cost of the query : {cost}".format(cost=cost))
    logger.info(
        "Time taken for this prompt : {time_elapsed}".format(
            time_elapsed=end_time - start_time
        )
    )

    # increment task counts
    increment_count(q_count)

    return res


def extract_dependencies(fd_dict):
    dependencies = set()  # Use a set to avoid duplicates
    for determinant, dependents in fd_dict.items():
        for dependent in dependents:
            dependencies.add((determinant, dependent))
    return dependencies


def get_filtered_functional_dependency(df):
    # take only first 15 columns and 1000 rows to analyse functional dependencies
    df = df.sample(n=min(1000, df.shape[0]), replace=False)
    df = df.iloc[:, :15]
    filtered_F, all_keys_sorted = analyze_functional_dependencies(df)

    if not filtered_F or not all_keys_sorted:
        return [], {}

    # Find the key with the most dependencies
    key_dependencies = {}
    for key, value in filtered_F:
        key = key[0]  # Assuming key is always a single-element tuple
        if key not in key_dependencies:
            key_dependencies[key] = set()
        key_dependencies[key].add(value)

    # Sort keys by number of dependencies, descending
    sorted_keys = sorted(
        key_dependencies.keys(), key=lambda k: len(key_dependencies[k]), reverse=True
    )

    # filter key based on rules
    # If key is first and numerical, it can be a key
    # If key is string type, it can be a key
    sorted_filtered_keys = []
    for key in sorted_keys:
        if df.columns.get_loc(key) == 0:
            sorted_filtered_keys.append(key)
        elif df[key].dtype == "object":
            sorted_filtered_keys.append(key)

    filtered_fd = {
        key: key_dependencies[key]
        for key in sorted_filtered_keys
        if key in key_dependencies
    }

    return sorted_filtered_keys, filtered_fd


def get_fd_hints(keys, fds):
    if not keys:
        return "No Clear Functional Dependencies Found in Target Table.\n\n"

    hint = "Functional Dependencies discovered from Target Table:\n"
    for key in keys:
        hint += "Functional Dependencies Associated with key " + key + " : "
        for v in fds[key]:
            hint += key + " -> " + v + " , "
        hint += "\n"
    hint += "\n"
    return hint
    # if not sorted_filtered_keys:
    #     return "No clear functional dependencies found"

    # hint = "Functional Dependencies discovered : \n"
    # for key in sorted_filtered_keys :
    #     hint += "Functional Dependencies Associated with key " + key + " : "
    #     for v in key_dependencies[key] :
    #         hint += key + " -> " + v + " , "
    #     hint += "\n"
    # if(hint == "Functional Dependencies discovered : \n") :
    #     return ""
    # else :
    #     return hint


def get_fd_hints_for_materialization(keys, fds, step):
    if not keys:
        return f"\n\nNo clear functional dependencies found in the intermediate_step{step} table.\n\n"
    hint = f"Functional dependencies discovered from the intermediate_step{step} table are :\n"
    for key in keys:
        hint += "Functional dependencies associated with key " + key + " : "
        for v in fds[key]:
            hint += key + " -> " + v + " , "
        hint += "\n"
    return hint


def get_key_column_hints(keys, step):
    if step <= 0:
        # For target table
        if not keys:
            hints = f"No clear key columns found in the target table."
        else:
            hints = f"Key columns discovered from the target table: {keys}\n"
    else:
        # For intermediate step
        if not keys:
            hints = f"No clear key columns found in the intermediate_step{step} table."
        else:
            hints = f"Key columns discovered from the intermediate_step{step} table : {keys}\n"
    return hints


def get_column_matching_hints(intermediate_df, target_df, step):
    """Compare the target df and ground truth df and return the matching columns
    Args:
        intermediate_df: the dataframe got by the transform pipeline
        target_df: the ground truth dataframe from the "target.csv" file.
        step: the step number of intermediate materialization
    """
    MATCHING_THRESHOLD = 0.95
    # Match schemas
    matcher = algorithms.Cupid()

    # Match schemas
    matches = valentine_match(intermediate_df, target_df, matcher)
    match_columns = []
    for ((_, col1), (_, col2)), score in matches.items():
        if score > MATCHING_THRESHOLD:
            match_columns.append((col1, col2))
    if match_columns:
        hint = ""
        for col1, col2 in match_columns:
            hint += f"Column {col1} from intermediate_step{step} table matches with column {col2} from target table.\n"
        return hint
    else:
        return f"\n\nNo matching columns found between intermediate_step{step} table and target tables.\n\n"


def calculate_score(gt_df, tgt_df):

    # parameters
    w1 = 1
    w2 = 1
    w3 = 1
    p = 1

    # Match Functional Dependencies
    key_gt, fd_gt = get_filtered_functional_dependency(gt_df)
    key_tgt, fd_tgt = get_filtered_functional_dependency(tgt_df)

    print("\n\n\nScore Calculation\n\n\n")

    print(fd_gt)
    print(key_gt)
    print("\n\nTarget : ")
    print(fd_tgt)
    print(key_tgt)

    dependencies_gt = extract_dependencies(fd_gt)
    dependencies_tgt = extract_dependencies(fd_tgt)

    overlapping_dependencies = dependencies_gt.intersection(dependencies_tgt)
    overlapping_keys = set(key_gt).intersection(key_tgt)

    score_fd = (
        len(overlapping_dependencies) / len(dependencies_gt)
        if (len(dependencies_gt) > 0)
        else 1
    )
    score_key = len(overlapping_keys) / len(key_gt) if (len(key_gt) > 0) else 1

    matcher = algorithms.Cupid()

    # Match schemas
    matches = valentine_match(gt_df, tgt_df, matcher)
    gt_df_columns = gt_df.columns

    gt_df_columns = set(gt_df.columns)
    matched_columns = set(match[0] for match in matches)
    # print("\n\n Matchings : ", matches)

    column_mapping_score = len(matched_columns) / len(gt_df_columns)

    score = pow(
        w1 * (score_fd**p) + w2 * (score_key**p) + w3 * (column_mapping_score) ** p,
        1 / p,
    )

    print([score_fd, score_key, column_mapping_score])
    return score


def calculate_score_cost(gt_df, tgt_df, cost_):

    # parameters
    w1 = 1
    w2 = 1
    w3 = 1
    p = 1

    # Match Functional Dependencies
    key_gt, fd_gt = get_filtered_functional_dependency(gt_df)
    key_tgt, fd_tgt = get_filtered_functional_dependency(tgt_df)

    print("\n\n\nScore Calculation\n\n\n")

    print(fd_gt)
    print(key_gt)
    print("\n\nTarget : ")
    print(fd_tgt)
    print(key_tgt)

    dependencies_gt = extract_dependencies(fd_gt)
    dependencies_tgt = extract_dependencies(fd_tgt)

    overlapping_dependencies = dependencies_gt.intersection(dependencies_tgt)
    overlapping_keys = set(key_gt).intersection(key_tgt)

    score_fd = (
        len(overlapping_dependencies) / len(dependencies_gt)
        if (len(dependencies_gt) > 0)
        else 1
    )
    score_key = len(overlapping_keys) / len(key_gt) if (len(key_gt) > 0) else 1

    matcher = algorithms.Cupid()

    # Match schemas
    matches = valentine_match(gt_df, tgt_df, matcher)
    gt_df_columns = gt_df.columns

    gt_df_columns = set(gt_df.columns)
    matched_columns = set(match[0] for match in matches)
    # print("\n\n Matchings : ", matches)

    column_mapping_score = len(matched_columns) / len(gt_df_columns)

    score = pow(
        w1 * (score_fd**p) + w2 * (score_key**p) + w3 * (column_mapping_score) ** p,
        1 / p,
    )

    print([score_fd, score_key, column_mapping_score])
    return score


if __name__ == "__main__":
    # generate all hints for join and aggregate

    main_folder = "autopipeline-benchmarks/github-pipelines"
    json_file_path = "data/chatgpt_github_ms.json"

    len_id = 2
    max_len_id = 2
    target_id = 0  # [11,18,22,25,62,10,16,31,38,5] # [18,2,32,33,96,16,27,78,91,18]
    max_target_id = 100
    target_per = 25
    is_perc = False
    hint_source = "v1"  # v1 or v2(Xuanmao's hints)

    target_length = int(max(3, 10 * 0.31342417815924284))
    source_length = int(max(3, 10 * 0.9682615757193975))

    join_flag = 1
    aggregate_flag = 1

    join_hints_truncate = [
        0.027387593197926163,
        0.8763891522960383,
        0.6923226156693141,
        0.8946066635038473,
        0.14038693859523377,
        0.8007445686755367,
    ]
    aggregate_hints_truncate = [0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1]

    task_list = get_test_cases_ids(
        json_file_path, len_id, max_len_id, target_id, max_target_id
    )

    for task in task_list:
        len_idx_target_idx = task[6:]
        (
            target_data_name,
            target_data_schema,
            target_samples,
            file_count,
            source_data_name_list,
            source_data_schema_list,
            source_samples_list,
        ) = get_test_info(json_file_path, len_idx_target_idx, main_folder)
        join_hints = get_hints(
            "join",
            hint_source,
            target_data_schema,
            file_count,
            source_data_name_list,
            source_data_schema_list,
            main_folder,
            len_idx_target_idx,
            join_flag,
            join_hints_truncate,
        )
        group_by_hints, aggregation_hints = get_hints(
            "group_by_aggregate",
            hint_source,
            target_data_schema,
            file_count,
            source_data_name_list,
            source_data_schema_list,
            main_folder,
            len_idx_target_idx,
            aggregate_flag,
            aggregate_hints_truncate,
        )

        print(join_hints, group_by_hints, aggregation_hints)
