import os
import time
import re
from pathlib import Path
from dataclasses import dataclass
import pdb

import pandas as pd
import logging
from datetime import datetime

# from model.aggregation.pwr import predict_columns
# from model.join.pwr import load_trained_model, predict_join_columns
# from quality.quality import get_df, data_summary, data_profiling, schema_quality, fd_quality, data_quality, \
# data_morpher, schema_matching
# from summary import load_tables, generate_transformation_hints
from util.utils import get_test_info

from test_scope import get_test_cases_ids

from hint import get_hints

# import summary
# from model.aggregation.pwr import load_trained_model, predict_columns
# from model.join.pwr import predict_join_columns

# from model.join.data import generate_features,is_single_column
# from model.aggregation.data import generate_features_for_column
import auto_suggest_llm_prompts as prt
import tiktoken
from quality.quality import analyze_functional_dependencies


from valentine import valentine_match, algorithms


# prt.get_prompt("join",                allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information,hints)
# prt.get_prompt("group_by_aggregate",  allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information,hints)
# prt.get_prompt("union",               allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,source_information,hints="")
# prt.get_python_script("python_script",allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count,ss,target_file_location)
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
        static_prompt = prt.get_next_operator_prompt(
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
            prompt = prt.get_next_operator_prompt_with_intermediate_materialization(
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
            prompt = prt.get_next_operator_prompt(
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
        static_prompt = prt.get_join_prompt(
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
        prompt = prt.get_join_prompt(
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
        static_prompt = prt.get_group_by_aggregate_prompt(
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
        prompt = prt.get_group_by_aggregate_prompt(
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
        static_prompt = prt.get_union_prompt(
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
        prompt = prt.get_union_prompt(
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
        static_prompt = prt.get_python_script(
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
            prompt = prt.get_python_script_with_intermediate_materialization(
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
            prompt = prt.get_python_script(
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


# def get_hints(prompt_type, hint_source,target_data_schema, file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx, hint_flag, hints_truncate) :
#     hints = []
#     if(hint_source == "v1") :
#         if(prompt_type == "join") :
#             hints = get_join_hints(file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx, hint_flag, hints_truncate)
#         if(prompt_type == "group_by_aggregate") :
#             hints = get_groupby_aggregate_hints(file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx, hint_flag, hints_truncate)
#         if(prompt_type == "get_next_operator") :
#             table_matching = get_table_matching(source_data_schema_list, source_data_name_list, target_data_schema)
#             column_table_mapping = get_column_table_mapping(target_data_schema, source_data_schema_list, source_data_name_list)
#             hints = [table_matching + "\n\n" + column_table_mapping]
#     elif(hint_source == "v2") :
#         tables = summary.load_tables(directory + "/length" + len_idx_target_idx)
#         # Load the models
#         join_model = load_trained_model('model/join/join_model.json')
#         key_model = load_trained_model('model/aggregation/key_model.json')

#         # Predict join column pairs
#         join_candidates = predict_join_columns(tables, join_model)
#         candidate_matching_columns = [(f"{t1}.{c1}", f"{t2}.{c2}", s) for (t1, c1), (t2, c2), s in join_candidates]

#         # Predict key columns for the target table
#         target_table_name = 'target'
#         target_df = tables[target_table_name]
#         # Fit LabelEncoder on all possible data types
#         all_data_types = ['int64', 'float64', 'object']  # Add more types if needed
#         label_encoder = LabelEncoder()
#         label_encoder.fit(all_data_types)
#         # Predict key columns for all tables
#         all_key_candidates = []
#         key_candidates = predict_columns(tables, key_model, label_encoder)
#         all_key_candidates.extend(key_candidates)

#         # print(candidate_matching_columns,'\n\n',all_key_candidates)

#         # Generate transformation hints
#         source_dfs = [tables[table] for table in tables if table != target_table_name]
#         hints = generate_transformation_hints(tables,source_dfs, target_df, mode='light', candidate_matching_columns=candidate_matching_columns, candidate_key_columns=key_candidates, type=prompt_type)
#         # print(hints)

#     else :
#         pass
#     return hints


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


# def get_column_description(t, c, features_seen, features):
#     col_key = f"{t}.{c}"
#     if col_key in features_seen:
#         return ""  # Already generated hint for this column

#     reasons = []
#     if "l" in features:
#         reasons.append("is on the left side of the table")
#     if "s" in features:
#         reasons.append("is sorted")
#     if "dvr" in features:
#         reasons.append("has many distinct values")

#     if reasons:
#         features_seen.add(col_key)
#         return f"{col_key} has a potential to be a key for JOIN since it " + ", ".join(reasons) + "."
#     return ""

# def get_join_hint_text(k, feat_dict, features_seen):
#     t1, c1 = k.split(' <-> ')[0].split('.')
#     t2, c2 = k.split(' <-> ')[1].split('.')
#     features = feat_dict.get(k, {})
#     join_reasons = []

#     # Join-level reasons
#     if "Jaccard Containment" in features:
#         join_reasons.append("have a high overlap in values")
#     if "Value Range Overlap" in features:
#         join_reasons.append("have high overlapping ranges")
#     if "Name Similarity" in features:
#         join_reasons.append("have similar names")

#     join_sentence = ""
#     if join_reasons:
#         join_sentence = (
#             f"{t1}.{c1} and Column {t2}.{c2} are good join candidates because they "
#             + ", ".join(join_reasons)
#             + "."
#         )

#     # Column-level reasoning
#     col1_features = {k: v["1"] for k, v in features.items() if isinstance(v, dict) and "1" in v}
#     col2_features = {k: v["2"] for k, v in features.items() if isinstance(v, dict) and "2" in v}

#     col1_sentence = get_column_description(t1, c1, features_seen, col1_features)
#     col2_sentence = get_column_description(t2, c2, features_seen, col2_features)

#     return "\n".join(filter(None, [join_sentence, col1_sentence, col2_sentence]))

# def get_join_hints(file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx, join_flag, join_hints_truncate) :
#     hints = ""
#     features = []
#     tables = load_tables(directory,source_data_name_list,len_idx_target_idx)
#     # print(tables)

#     # dictionary that stores each attribute's successful features
#     # i.e if attribute col1<->col2 satisfies the feature x it should have key="col1,col2" : value=[(feature_name,feature_value)]
#     # at the end sort the dictionary based on length of values satisfied.
#     feat_dict = {}

#     for table_name1, table_name2 in combinations(tables.keys(), 2):
#         table1 = tables[table_name1]
#         table2 = tables[table_name2]
#         columns1 = table1.columns
#         columns2 = table2.columns
#         total_columns1 = len(columns1)
#         total_columns2 = len(columns2)

#         for col1 in columns1 :
#             for col2 in columns2 :
#                 if(table1[col1].dtype == table2[col2].dtype) :
#                     # print(col1,col2)
#                     hint = ' - '
#                     pos1 = columns1.get_loc(col1)
#                     pos2 = columns2.get_loc(col2)
#                     feature = generate_features(table1[col1], table2[col2], table1, table2, pos1, pos2, total_columns1, total_columns2, is_single_column([(col1, col2)]))
#                     # generate table1.col1 <-> table2.col2 as a key
#                     fq = get_truncated_join_feature(feature,join_flag,join_hints_truncate)
#                     if(col1 == col2) :
#                         fq["priority"] = 1
#                     else : fq["priority"] = 0
#                     # print(fq)
#                     if(len(fq) > 3) :

#                         feat_dict[f"{table_name1}.{col1} <-> {table_name2}.{col2}"] = get_truncated_join_feature(feature,join_flag,join_hints_truncate)

#                     if(join_flag == 0) :
#                         if(check_feature_join(feature, join_flag, join_hints_truncate)) :
#                             hint+=table_name1+'.'+col1+'<->'+table_name2+'.'+col2+' : '
#                             hint+='''(distinct_value_ratio of {t1}.{c1} : {f[0]}, distinct_value_ratio of {t2}.{c2} : {f[1]}),value-overlap: (Jaccard Similarity : {f[2]}, Jaccard containment : {f[3]}),value-range-overlap: {f[4]},leftness of {t1}.{c1} : {f[6]},leftness of {t2}.{c2} : {f[7]},sortedness of {t1}.{c1} : {f[8]},sortedness of {t2}.{c2} : {f[9]},ratio of row-count : {f[10]})\n'''.format(c1=col1,c2=col2,t1=table_name1,t2=table_name2,f=feature)
#                             hints += hint


#     if(join_flag) :

#         # todo change the implementation to have two functionns one for the key-value pair and one for the text representation.
#         # process the dictionary
#         # sort the dictionary keys based on length of values
#         # print(feat_dict)
#         ## uncomment here
#         # seen_columns = set()
#         # hints = ""
#         # cnt = 0
#         # for k in sorted(feat_dict, key=lambda k: (feat_dict[k].get('priority', 0) == 0, len(feat_dict[k])), reverse=True):
#         #     cnt+=1
#         #     if(cnt > 10) :
#         #         break
#         #     hint = get_join_hint_text(k, feat_dict, seen_columns)
#         #     if hint:
#         #         hints += hint + "\n\n"

#         # process column-pair based features


#         # process column based features

#         cnt = 0
#         for k in sorted(feat_dict, key=lambda k: (feat_dict[k].get('priority', 0) == 0, len(feat_dict[k])), reverse=True):
#             cnt+=1
#             hint = f' - {k.replace(' <-> ', ' POTENTIAL JOIN ')} ' + " { "

#             #todo create two functions, one for key-value pair and one for the text representation.
#             t1,c1,t2,c2 = k.split(' <-> ')[0].split('.')[0],k.split(' <-> ')[0].split('.')[1],k.split(' <-> ')[1].split('.')[0], k.split(' <-> ')[1].split('.')[1]
#             # print(t1,c1,t2,c2)
#             # print(feat_dict[k])
#             for ky,v in feat_dict[k].items() :
#                 if(ky == "dvr") :
#                     if("1" in v.keys()) :
#                         hint += f"Distinct Value Ratio of {t1}.{c1} : {round(v["1"],2)} , "
#                     if("2" in v.keys()) :
#                         hint += f"Distinct Value Ratio of {t2}.{c2} : {round(v["2"],2)} , "
#                 elif(ky == "l") :
#                     if("1" in v.keys()) :
#                         hint += f"Leftness of {t1}.{c1} : {round(v["1"],2)} , "
#                     if("2" in v.keys()) :
#                         hint += f"Leftness of {t2}.{c2} : {round(v["2"],2)} , "
#                     # hint += f"Leftness of {t1}.{c1} : {round(v["1"],2)}, Leftness of {t2}.{c2} : {round(v["2"],2)}"
#                 elif(ky == "s") :
#                     if("1" in v.keys()) :
#                         hint += f"Sortedness of {t1}.{c1} : {round(v["1"],2)}"
#                     if("2" in v.keys()) :
#                         hint += f"Sortedness of {t2}.{c2} : {round(v["2"],2)}"
#                     # hint += f"Sortedness of {t1}.{c1} : {round(v["1"],2)}, Sortedness of {t2}.{c2} : {round(v["2"],2)}"
#                 else :
#                     hint += f"{ky} : {round(v,2)}"
#                 hint += " , "

#             hint = hint[:-3] + " }"
#             # print(hint)
#             hints += hint + "\n"
#             if(cnt > 10) :
#                 break


#         # add the hint string
#         # print(feat_dict)

#     # print(hints)
#     return [hints]

#     # return dict(sorted(feat_dict.items(), key=lambda item: (item[1].get('priority', 0) == 0, len(item[1])), reverse=True))

# def get_truncated_join_feature(f,join_flag, jht) :
#     feature_list = {}
#     if(join_flag) :
#         if f[0] >= jht[0] or f[1] >= jht[0]:
#             feature_list["dvr"] = {}
#             if f[0] >= jht[0]:
#                 feature_list["dvr"]["1"] = f[0]
#             if f[1] >= jht[0]:
#                 feature_list["dvr"]["2"] = f[1]

#         if(f[2] >= jht[1]) :
#             feature_list["Jaccard Similarity"] = f[2]

#         if(f[3] >= jht[2]) :
#             feature_list["Jaccard Containment"] = f[3]

#         if(f[4] >= jht[3]) : # check logic and change rule, we need high for the join candidacy
#             feature_list["Value Range Overlap"] = f[4]

#        # Leftness
#         if f[6] >= jht[4] or f[7] >= jht[4]:
#             feature_list["l"] = {}
#             if f[6] >= jht[4]:
#                 feature_list["l"]["1"] = f[6]
#             if f[7] >= jht[4]:
#                 feature_list["l"]["2"] = f[7]

#         # Sortedness
#         if jht[5] > 0.5:
#             if f[8] or f[9]:
#                 feature_list["s"] = {}
#                 if f[8]:
#                     feature_list["s"]["1"] = f[8]
#                 if f[9]:
#                     feature_list["s"]["2"] = f[9]

#     return feature_list

# def check_feature_join(f, join_flag, jht) :
#     if(join_flag) :
#         # distinct_value_ratio
#         if(f[0] < jht[0] or f[1] < jht[0]) :
#             return False

#         # value overlap
#         # Jaccard similarity
#         if(f[2] < jht[1]) :
#             return False
#         # Jaccard Containment
#         if(f[3] < jht[2]) :
#             return False

#         # value_range_overlap
#         if(f[4] < jht[3]) :
#             return False

#         # leftness
#         if(f[6] < jht[4] or f[7] < jht[4]) :
#             return False

#         # sortedness
#         if((jht[5] > 0.5)) :
#             if((not f[8]) or (not f[9])) :
#                 return False

#     return True


# def get_group_by_hint(colname, features_seen, features):
#     if colname in features_seen:
#         return ""
#     reasons = []
#     if "Distinct Value Ratio" in features:
#         reasons.append("it has many repeated values")
#     if "Leftness" in features:
#         reasons.append("it is on the left side of the table")
#     if "Emptiness" in features:
#         reasons.append("it has less null values")
#     if "Peak Frequency" in features:
#         reasons.append("it has one value that was repeated many times")
#     if features.get("datatype") == "String":
#         reasons.append("its datatype is STRING")

#     if reasons:
#         features_seen.add(colname)
#         return f"{colname} has a potential to be a GROUP BY key because " + ", ".join(reasons) + "."
#     return ""


# def get_aggregation_function_hint(directory, column_name):
#     # Parse table and column
#     print(directory, column_name)
#     try:
#         source_name, col = column_name.split('.')
#     except ValueError:
#         return ""  # Malformed column name

#     if not source_name.startswith("Source"):
#         return ""

#     try:
#         # Extract dataset ID and file index
#         dataset_id = source_name.split('_')[0][6:] + "_" + source_name.split('_')[1]
#         file_index = source_name.split('_')[2]
#     except IndexError:
#         return "IndexError"

#     # Construct file paths
#     source_file = os.path.join(directory, f'length{dataset_id}', f'test_{file_index}.csv')
#     target_file = os.path.join(directory, f'length{dataset_id}', 'target.csv')

#     print(source_file, target_file)

#     # Check file existence
#     if not os.path.exists(source_file) or not os.path.exists(target_file):
#         return "File not exist"

#     try:
#         source_df = pd.read_csv(source_file)
#         target_df = pd.read_csv(target_file)
#     except Exception:
#         return "File did not get read"

#     if col not in target_df.columns:
#         return "column is not there"

#     # Infer datatypes
#     source_dtype = source_df[col].dtype if col in source_df.columns else None
#     target_dtype = target_df[col].dtype

#     print(source_dtype, target_dtype)

#     if pd.api.types.is_float_dtype(target_dtype):
#         if pd.api.types.is_integer_dtype(source_dtype):
#             return f" The recommended aggregation function is `avg`"
#         elif pd.api.types.is_float_dtype(source_dtype):
#             return f" The recommended aggregation functions are `avg`, `sum`, `min`, `max`."
#     elif pd.api.types.is_integer_dtype(target_dtype):
#         if pd.api.types.is_string_dtype(source_dtype):
#             return f" The recommended aggregation function is `count`"
#         elif pd.api.types.is_integer_dtype(source_dtype):
#             return f" The recommended aggregation functions are `sum`, `count`, `min`, `max`."

#     return ""


# def get_aggregate_hint(colname, features_seen, features):
#     if colname in features_seen:
#         return ""
#     reasons = []
#     if "Distinct Value Ratio" in features:
#         reasons.append("it has many distinct values")
#     if "Leftness" in features:
#         reasons.append("it is on the right side of the table")
#     if "Emptiness" in features:
#         reasons.append("it has many null values")
#     if "Peak Frequency" in features:
#         reasons.append("its most frequent value appears rarely")
#     if features.get("datatype") == "Numerical":
#         reasons.append("its datatype is NUMERIC")

#     if reasons:
#         features_seen.add(colname)
#         return f"{colname} has a potential to be an AGGREGATE column because " + ", ".join(reasons) + "."
#     return ""

# def get_groupby_aggregate_hints(file_count,source_data_name_list,source_data_schema_list,directory,len_idx_target_idx, aggregate_flag, aggregate_hints_truncate) :
#     hints = ""
#     features = []
#     tables = load_tables(directory,source_data_name_list,len_idx_target_idx)
#     feat_dict_gb = {}
#     feat_dict_aggregate = {}

#     all_data_types = ['int64', 'float64', 'object']  # Add more types if needed
#     label_encoder = LabelEncoder()
#     label_encoder.fit(all_data_types)

#     for table_name, table in tables.items():
#         columns = table.columns
#         total_columns = len(columns)

#         for pos, col_name in enumerate(columns):
#             if(table[col_name].dtype == "bool") :
#                 continue
#             hint = ' - '
#             col = table[col_name]
#             # Generate features
#             feature = generate_features_for_column(col, col_name, pos, total_columns,label_encoder)
#             # print(feature)

#             #group by
#             fq = get_truncated_aggreggation_features(feature,aggregate_flag, aggregate_hints_truncate,1)
#             if(len(fq) > 2) :
#                 feat_dict_gb[f"{table_name}.{col_name}"] = fq
#             #aggrregate
#             fq = get_truncated_aggreggation_features(feature,aggregate_flag, aggregate_hints_truncate, 0)
#             if(len(fq) > 2) :
#                 feat_dict_aggregate[f"{table_name}.{col_name}"] = fq

#             if(aggregate_flag == 0) :
#                 if(check_feature_group_by(feature, aggregate_flag, aggregate_hints_truncate)) :
#                     hint += table_name+'.'+col_name+ ' : '
#                     hint += '''(Distinct value count : {f[0]}, Distinct Value Ratio : {f[1]}, Column Data Type : {f[2]}, Leftness : {f[3]}, Emptiness : {f[4]}, Value_Range : {f[5]}, ratio of distinct value count to range : {f[6]}, Peak Frequency : {f[7]})\n'''.format(f = feature)
#                     hints += hint

#     if(aggregate_flag) :
#         # print(feat_dict_gb,"\n\n", feat_dict_aggregate)
#         # hints = ""

#         # # === GROUP BY HINTS ===
#         # hints += "Group By Candidates:\n"
#         # gb_seen = set()
#         # gb_keys_sorted = sorted(feat_dict_gb, key=lambda k: len(feat_dict_gb[k]), reverse=True)
#         # for k in islice(gb_keys_sorted, 10):
#         #     if len(feat_dict_gb[k]) > 0:

#         #         hint = get_group_by_hint(k, gb_seen, feat_dict_gb[k])
#         #         print( k, feat_dict_gb[k], hint)
#         #         if hint:
#         #             hints += " - " + hint + "\n"

#         # # === AGGREGATE HINTS ===
#         # hints += "\nAggregation Candidates:\n"
#         # agg_seen = set()
#         # agg_keys_sorted = sorted(feat_dict_aggregate, key=lambda k: len(feat_dict_aggregate[k]), reverse=True)
#         # for k in islice(agg_keys_sorted, 10):
#         #     if len(feat_dict_aggregate[k]) > 0:
#         #         hint = get_aggregate_hint(k, agg_seen, feat_dict_aggregate[k])
#         #         hint += get_aggregation_function_hint(directory,k)
#         #         if hint:
#         #             hints += " - " + hint + "\n"


#     # return [hints]


#         print(feat_dict_gb, feat_dict_aggregate)
#         hints += "Group By Candidates : \n"
#         cnt = 0
#         for k in sorted(feat_dict_gb,key=lambda k: len(feat_dict_gb[k]), reverse=True) :
#             cnt += 1
#             if (len(feat_dict_gb[k]) > 0) :
#                 hint = f" - {k}  " + " { "
#                 for ky,v in feat_dict_gb[k].items() :
#                     hint += f"{ky} : {v} , "
#                 hint = hint[:-3] + " }\n"
#                 hints += hint
#                 if(cnt > 10) :
#                     break

#         hints += "Aggregation Candidates : \n"
#         cnt = 0
#         for k in sorted(feat_dict_aggregate,key=lambda k: len(feat_dict_aggregate[k]), reverse=True) :
#             cnt += 1
#             if (len(feat_dict_aggregate[k]) > 0) :
#                 hint = f" - {k} : " + " { "
#                 for ky,v in feat_dict_aggregate[k].items() :
#                     hint += f"{ky} : {v} , "
#                 hint = hint[:-3] + " }"
#                 hints += hint
#                 if(cnt > 10) :
#                     break
#     # print(hints)
#     return [hints]
#     # return dict(sorted(feat_dict_gb.items(), key=lambda item: len(item[1]), reverse=True)),dict(sorted(feat_dict_aggregate.items(), key=lambda item: len(item[1]), reverse=True))

# def get_truncated_aggreggation_features(f, flag, aht, group_by_flag) :
#     feature_list = {}
#     if(flag) :
#         if(group_by_flag) :
#             # [dvr_ub,dvr_lb, leftness_ub,leftness_lb, emptiness_ub,emptiness_lb, peak_frequency_ub, peak_frequency_lb,value_range_ub, value_range_lb]
#             if(f[1] <= aht[1]) : # low distinct value ratio
#                 feature_list["Distinct Value Ratio"] = round(f[1],2)
#             if(f[3] >= aht[2]) : # high leftness
#                 feature_list["Leftness"] = round(f[2],2)
#             if(f[4] <= aht[5]) : # low emptines
#                 feature_list["Emptiness"] = round(f[4],2)
#             if(f[7] >= aht[6]) : # high peak frequerncy
#                 feature_list["Peak Frequency"] = round(f[7],2)
#             if(f[2] in [0,1] and f[6] <= aht[9]) : # small value range for group by column
#                 feature_list["Value Range"] = round(f[5],2)
#             if(f[2] in [2]) : # string datatype
#                 feature_list["datatype"] = "String"

#         else : # aggregation feature
#             # [dvr_ub,dvr_lb, leftness_ub,leftness_lb, emptiness_ub,emptiness_lb, peak_frequency_ub, peak_frequency_lb,value_range_ub, value_range_lb]
#             # [01, 23, 45, 67, 89]
#             # [0.9,0.1,0.9,0.1,0.9,0.1,0.9,0.1,0.9,0.1]
#             if(f[1] >= aht[0]) : # high distinct value ratio
#                 feature_list["Distinct Value Ratio"] = round(f[1],2)
#             if(f[3] <= aht[3]) : # low leftness
#                 feature_list["Leftness"] = round(f[2],2)
#             if(f[4] >= aht[4]) : # may have high emptines
#                 feature_list["Emptiness"] = round(f[4],2)
#             if(f[7] <= aht[7]) : # may have low peak frequerncy
#                 feature_list["Peak Frequency"] = round(f[7],2)
#             if(f[2] in [0,1] and f[6] >= aht[8]) : # large value range for group by column
#                 feature_list["Value Range"] = round(f[5],2)
#             if(f[2] in [0,1]) :
#                 feature_list["datatype"] = "Numerical"
#     # print(feature_list)
#     return feature_list

# def check_feature_group_by(f,flag,aht) :
#     if(flag) :
#         # distinct_value_ratio
#         if(f[1] < aht[0]) :
#             return False
#         # leftness
#         if(f[3] < aht[1]) :
#             return False
#         # emptiness
#         if(f[4] > aht[2]) :
#             return False
#         # peak frequency
#         if(f[7] < aht[3]) :
#             return False


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
