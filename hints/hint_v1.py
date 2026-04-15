import ast
import os

from itertools import combinations
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from itertools import islice
from model.join.data import generate_features, is_single_column
from model.aggregation.data import generate_features_for_column


def load_tables(directory, source_data_name_list, len_idx_target_idx):
    tables = {}
    for i in range(len(source_data_name_list)):
        tables[source_data_name_list[i]] = pd.read_csv(
            os.path.join(
                directory, "length" + len_idx_target_idx + "/test_" + str(i) + ".csv"
            )
        )
        tables[source_data_name_list[i]] = tables[source_data_name_list[i]].drop(
            tables[source_data_name_list[i]].columns[0], axis=1
        )
    return tables


def get_table_matching(
    source_data_schema_list, source_data_name_list, target_data_schema
):
    # Convert string representations of lists to actual lists
    source_data_schema_list = [
        ast.literal_eval(schema) for schema in source_data_schema_list
    ]
    target_data_schema = ast.literal_eval(target_data_schema)

    table_matchings = []
    num_sources = len(source_data_schema_list)

    for i in range(num_sources):
        for j in range(i + 1, num_sources):
            set1, set2 = set(source_data_schema_list[i]), set(
                source_data_schema_list[j]
            )
            name1, name2 = source_data_name_list[i], source_data_name_list[j]

            if set1.issubset(set2) and len(set2) == len(set1) + 1:
                table_matchings.append(
                    f"{len(set1)}/{len(set2)} columns of {name1} are covered by {name2} and {len(set2)}/{len(set2)} columns of {name2} are covered by {name1} suggesting UNION."
                )
            elif set2.issubset(set1) and len(set1) == len(set2) + 1:
                table_matchings.append(
                    f"{len(set2)}/{len(set1)} columns of {name2} are covered by {name1} and {len(set1)}/{len(set1)} columns of {name1} are covered by {name2} suggesting UNION."
                )

    return "\n".join(table_matchings)


def get_column_table_mapping(
    target_data_schema, source_data_schema_list, source_data_name_list
):
    # Convert string representations of lists to actual lists
    source_data_schema_list = [
        ast.literal_eval(schema) for schema in source_data_schema_list
    ]
    target_data_schema = ast.literal_eval(target_data_schema)

    # Mapping target columns to source tables
    column_source_mapping = {col: [] for col in target_data_schema}

    for i, source_schema in enumerate(source_data_schema_list):
        for col in target_data_schema:
            # Generalized substring match
            if any(
                source_col in col or col in source_col for source_col in source_schema
            ):
                column_source_mapping[col].append(source_data_name_list[i])

    # Printing the result
    mappings = ""
    for col, sources in column_source_mapping.items():
        if len(sources) > 0:
            mappings += f"{col} is available in {', '.join(sources)}\n"
        else:
            mappings += f"{col} column_name is not available in any source directly\n"
    # print(mappings)
    return mappings


def get_column_description(t, c, features_seen, features):
    col_key = f"{t}.{c}"
    if col_key in features_seen:
        return ""  # Already generated hint for this column

    reasons = []
    if "l" in features:
        reasons.append("is on the left side of the table")
    if "s" in features:
        reasons.append("is sorted")
    if "dvr" in features:
        reasons.append("has many distinct values")

    if reasons:
        features_seen.add(col_key)
        return (
            f"{col_key} has a potential to be a key for JOIN since it "
            + ", ".join(reasons)
            + "."
        )
    return ""


def get_join_hint_text(k, feat_dict, features_seen):
    t1, c1 = k.split(" <-> ")[0].split(".")
    t2, c2 = k.split(" <-> ")[1].split(".")
    features = feat_dict.get(k, {})
    join_reasons = []

    # Join-level reasons
    if "Jaccard Containment" in features:
        join_reasons.append("have a high overlap in values")
    if "Value Range Overlap" in features:
        join_reasons.append("have high overlapping ranges")
    if "Name Similarity" in features:
        join_reasons.append("have similar names")

    join_sentence = ""
    if join_reasons:
        join_sentence = (
            f"{t1}.{c1} and Column {t2}.{c2} are good join candidates because they "
            + ", ".join(join_reasons)
            + "."
        )

    # Column-level reasoning
    col1_features = {
        k: v["1"] for k, v in features.items() if isinstance(v, dict) and "1" in v
    }
    col2_features = {
        k: v["2"] for k, v in features.items() if isinstance(v, dict) and "2" in v
    }

    col1_sentence = get_column_description(t1, c1, features_seen, col1_features)
    col2_sentence = get_column_description(t2, c2, features_seen, col2_features)

    return "\n".join(filter(None, [join_sentence, col1_sentence, col2_sentence]))


def get_join_hints(
    hint_source,
    file_count,
    source_data_name_list,
    source_data_schema_list,
    directory,
    len_idx_target_idx,
    join_flag,
    join_hints_truncate,
):
    hints = ""
    features = []
    tables = load_tables(directory, source_data_name_list, len_idx_target_idx)
    # print(tables)

    # dictionary that stores each attribute's successful features
    # i.e if attribute col1<->col2 satisfies the feature x it should have key="col1,col2" : value=[(feature_name,feature_value)]
    # at the end sort the dictionary based on length of values satisfied.
    feat_dict = {}

    # print("Generating join hints...")

    for table_name1, table_name2 in combinations(tables.keys(), 2):
        table1 = tables[table_name1]
        table2 = tables[table_name2]
        columns1 = table1.columns
        columns2 = table2.columns
        total_columns1 = len(columns1)
        total_columns2 = len(columns2)

        for col1 in columns1:
            for col2 in columns2:
                if table1[col1].dtype == table2[col2].dtype:
                    # print(col1,col2)
                    hint = " - "
                    pos1 = columns1.get_loc(col1)
                    pos2 = columns2.get_loc(col2)
                    feature = generate_features(
                        table1[col1],
                        table2[col2],
                        table1,
                        table2,
                        pos1,
                        pos2,
                        total_columns1,
                        total_columns2,
                        is_single_column([(col1, col2)]),
                    )
                    # generate table1.col1 <-> table2.col2 as a key
                    fq = get_truncated_join_feature(
                        feature, join_flag, join_hints_truncate
                    )
                    if col1 == col2:
                        fq["priority"] = 1
                    else:
                        fq["priority"] = 0
                    # print(fq)
                    if len(fq) > 3:

                        feat_dict[f"{table_name1}.{col1} <-> {table_name2}.{col2}"] = (
                            get_truncated_join_feature(
                                feature, join_flag, join_hints_truncate
                            )
                        )

                    if join_flag == 0:
                        if check_feature_join(feature, join_flag, join_hints_truncate):
                            hint += (
                                table_name1
                                + "."
                                + col1
                                + " <-> "
                                + table_name2
                                + "."
                                + col2
                                + " : "
                            )
                            hint += """(distinct_value_ratio of {t1}.{c1} : {f[0]}, distinct_value_ratio of {t2}.{c2} : {f[1]}),value-overlap: (Jaccard Similarity : {f[2]}, Jaccard containment : {f[3]}),value-range-overlap: {f[4]},leftness of {t1}.{c1} : {f[6]},leftness of {t2}.{c2} : {f[7]},sortedness of {t1}.{c1} : {f[8]},sortedness of {t2}.{c2} : {f[9]},ratio of row-count : {f[10]})\n""".format(
                                c1=col1,
                                c2=col2,
                                t1=table_name1,
                                t2=table_name2,
                                f=feature,
                            )
                            hints += hint

    if join_flag:

        # todo change the implementation to have two functionns one for the key-value pair and one for the text representation.
        # process the dictionary
        # sort the dictionary keys based on length of values
        # print(feat_dict)
        ## uncomment here
        if hint_source == "v1_text":
            seen_columns = set()
            hints = ""
            cnt = 0
            for k in sorted(
                feat_dict,
                key=lambda k: (feat_dict[k].get("priority", 0) == 0, len(feat_dict[k])),
                reverse=True,
            ):
                cnt += 1
                if cnt > 10:
                    break
                hint = get_join_hint_text(k, feat_dict, seen_columns)
                if hint:
                    hints += hint + "\n\n"

        # process column-pair based features

        # process column based features

        # print(feat_dict)

        if hint_source == "v1_kv":
            cnt = 0
            for k in sorted(
                feat_dict,
                key=lambda k: (feat_dict[k].get("priority", 0) == 0, len(feat_dict[k])),
                reverse=True,
            ):
                cnt += 1
                if cnt > 10:
                    break
                hint = f' - {k.replace(" <-> ", " POTENTIAL JOIN ")} ' + " { "

                # todo create two functions, one for key-value pair and one for the text representation.
                t1, c1, t2, c2 = (
                    k.split(" <-> ")[0].split(".")[0],
                    k.split(" <-> ")[0].split(".")[1],
                    k.split(" <-> ")[1].split(".")[0],
                    k.split(" <-> ")[1].split(".")[1],
                )
                # print(t1,c1,t2,c2)
                # print(feat_dict[k])
                for ky, v in feat_dict[k].items():
                    if ky == "dvr":
                        if "1" in v.keys():
                            hint += f"Distinct Value Ratio of {t1}.{c1} : {round(v['1'],2)} , "
                        if "2" in v.keys():
                            hint += f"Distinct Value Ratio of {t2}.{c2} : {round(v['2'],2)} , "
                    elif ky == "l":
                        if "1" in v.keys():
                            hint += f"Leftness of {t1}.{c1} : {round(v['1'],2)} , "
                        if "2" in v.keys():
                            hint += f"Leftness of {t2}.{c2} : {round(v['2'],2)} , "
                        # hint += f"Leftness of {t1}.{c1} : {round(v["1"],2)}, Leftness of {t2}.{c2} : {round(v["2"],2)}"
                    elif ky == "s":
                        if "1" in v.keys():
                            hint += f"Sortedness of {t1}.{c1} : {round(v['1'],2)}"
                        if "2" in v.keys():
                            hint += f"Sortedness of {t2}.{c2} : {round(v['2'],2)}"
                        # hint += f"Sortedness of {t1}.{c1} : {round(v["1"],2)}, Sortedness of {t2}.{c2} : {round(v["2"],2)}"
                    else:
                        hint += f"{ky} : {round(v,2)}"
                    hint += " , "

                hint = hint[:-3] + " }"
                # print(hint)
                hints += hint + "\n"

        # add the hint string
        # print(feat_dict)

    # print(hints)
    return [hints]

    # return dict(sorted(feat_dict.items(), key=lambda item: (item[1].get('priority', 0) == 0, len(item[1])), reverse=True))


def get_truncated_join_feature(f, join_flag, jht):
    feature_list = {}
    # print(join_flag, jht)
    if join_flag:
        if f[0] >= jht[0] or f[1] >= jht[0]:
            feature_list["dvr"] = {}
            if f[0] >= jht[0]:
                feature_list["dvr"]["1"] = f[0]
            if f[1] >= jht[0]:
                feature_list["dvr"]["2"] = f[1]

        if f[2] >= jht[1]:
            feature_list["Jaccard Similarity"] = f[2]

        if f[3] >= jht[2]:
            feature_list["Jaccard Containment"] = f[3]

        if (
            f[4] >= jht[3]
        ):  # check logic and change rule, we need high for the join candidacy
            feature_list["Value Range Overlap"] = f[4]

        # Leftness
        if (1 - f[7]) >= jht[4] or (1 - f[9]) >= jht[4]:
            feature_list["l"] = {}
            if (1 - f[7]) >= jht[4]:
                feature_list["l"]["1"] = f[6]
            if (1 - f[9]) >= jht[4]:
                feature_list["l"]["2"] = f[7]

        # Sortedness
        if jht[5] > 0.5:
            if f[10] or f[11]:
                feature_list["s"] = {}
                if f[10]:
                    feature_list["s"]["1"] = f[8]
                if f[11]:
                    feature_list["s"]["2"] = f[9]

    return feature_list


def check_feature_join(f, join_flag, jht):
    if join_flag:
        # distinct_value_ratio
        if f[0] < jht[0] and f[1] < jht[0]:
            return False

        # value overlap
        # Jaccard similarity
        if f[2] < jht[1]:
            return False
        # Jaccard Containment
        if f[3] < jht[2]:
            return False

        # value_range_overlap
        if f[4] < jht[3]:
            return False

        # leftness
        if (1 - f[7]) < jht[4] or (1 - f[9]) < jht[4]:
            return False

        # sortedness
        if jht[5] > 0.5:
            if (not f[10]) or (not f[11]):
                return False

    return True


def get_group_by_hint(colname, features_seen, features):
    if colname in features_seen:
        return ""
    reasons = []
    if "Distinct Value Ratio" in features:
        reasons.append("it has many repeated values")
    if "Leftness" in features:
        reasons.append("it is on the left side of the table")
    if "Emptiness" in features:
        reasons.append("it has less null values")
    if "Peak Frequency" in features:
        reasons.append("it has one value that was repeated many times")
    if features.get("datatype") == "String":
        reasons.append("its datatype is STRING")

    if reasons:
        features_seen.add(colname)
        return (
            f"{colname} has a potential to be a GROUP BY key because "
            + ", ".join(reasons)
            + "."
        )
    return ""


def get_aggregation_function_hint(directory, column_name):
    # Parse table and column
    # print(directory, column_name)
    try:
        source_name, col = column_name.split(".")
    except ValueError:
        return ""  # Malformed column name

    if not source_name.startswith("Source"):
        return ""

    try:
        # Extract dataset ID and file index
        dataset_id = source_name.split("_")[0][6:] + "_" + source_name.split("_")[1]
        file_index = source_name.split("_")[2]
    except IndexError:
        return "IndexError"

    # Construct file paths
    source_file = os.path.join(
        directory, f"length{dataset_id}", f"test_{file_index}.csv"
    )
    target_file = os.path.join(directory, f"length{dataset_id}", "target.csv")

    # print(source_file, target_file)

    # Check file existence
    if not os.path.exists(source_file) or not os.path.exists(target_file):
        return "File not exist"

    try:
        source_df = pd.read_csv(source_file)
        target_df = pd.read_csv(target_file)
    except Exception:
        return "File did not get read"

    if col not in target_df.columns:
        return "column is not there"

    # Infer datatypes
    source_dtype = source_df[col].dtype if col in source_df.columns else None
    target_dtype = target_df[col].dtype

    # print(source_dtype, target_dtype)

    if pd.api.types.is_float_dtype(target_dtype):
        if pd.api.types.is_integer_dtype(source_dtype):
            return f" The recommended aggregation function is `avg`"
        elif pd.api.types.is_float_dtype(source_dtype):
            return f" The recommended aggregation functions are `avg`, `sum`, `min`, `max`."
    elif pd.api.types.is_integer_dtype(target_dtype):
        if pd.api.types.is_string_dtype(source_dtype):
            return f" The recommended aggregation function is `count`"
        elif pd.api.types.is_integer_dtype(source_dtype):
            return f" The recommended aggregation functions are `sum`, `count`, `min`, `max`."

    return ""


def get_aggregate_hint(colname, features_seen, features):
    if colname in features_seen:
        return ""
    reasons = []
    if "Distinct Value Ratio" in features:
        reasons.append("it has many distinct values")
    if "Leftness" in features:
        reasons.append("it is on the right side of the table")
    if "Emptiness" in features:
        reasons.append("it has many null values")
    if "Peak Frequency" in features:
        reasons.append("its most frequent value appears rarely")
    if features.get("datatype") == "Numerical":
        reasons.append("its datatype is NUMERIC")

    if reasons:
        features_seen.add(colname)
        return (
            f"{colname} has a potential to be an AGGREGATE column because "
            + ", ".join(reasons)
            + "."
        )
    return ""


def get_groupby_aggregate_hints(
    hint_source,
    file_count,
    source_data_name_list,
    source_data_schema_list,
    directory,
    len_idx_target_idx,
    aggregate_flag,
    aggregate_hints_truncate,
):
    hints = ""
    features = []
    tables = load_tables(directory, source_data_name_list, len_idx_target_idx)
    feat_dict_gb = {}
    feat_dict_aggregate = {}

    all_data_types = ["int64", "float64", "object"]  # Add more types if needed
    label_encoder = LabelEncoder()
    label_encoder.fit(all_data_types)

    for table_name, table in tables.items():
        columns = table.columns
        total_columns = len(columns)

        for pos, col_name in enumerate(columns):
            if table[col_name].dtype == "bool":
                continue
            hint = " - "
            col = table[col_name]
            # Generate features
            feature = generate_features_for_column(
                col, col_name, pos, total_columns, label_encoder
            )
            # print(feature)

            # group by
            fq = get_truncated_aggreggation_features(
                feature, aggregate_flag, aggregate_hints_truncate, 1
            )
            if len(fq) > 2:
                feat_dict_gb[f"{table_name}.{col_name}"] = fq
            # aggrregate
            fq = get_truncated_aggreggation_features(
                feature, aggregate_flag, aggregate_hints_truncate, 0
            )
            if len(fq) > 2:
                feat_dict_aggregate[f"{table_name}.{col_name}"] = fq

            if aggregate_flag == 0:
                if check_feature_group_by(
                    feature, aggregate_flag, aggregate_hints_truncate
                ):
                    hint += table_name + "." + col_name + " : "
                    hint += """(Distinct value count : {f[0]}, Distinct Value Ratio : {f[1]}, Column Data Type : {f[2]}, Leftness : {f[3]}, Emptiness : {f[4]}, Value_Range : {f[5]}, ratio of distinct value count to range : {f[6]}, Peak Frequency : {f[7]})\n""".format(
                        f=feature
                    )
                    hints += hint

    if aggregate_flag:
        # print(feat_dict_gb,"\n\n", feat_dict_aggregate)
        hints = ""

        # === GROUP BY HINTS ===
        if hint_source == "v1_text":
            hints += "Group By Candidates:\n"
            gb_seen = set()
            gb_keys_sorted = sorted(
                feat_dict_gb, key=lambda k: len(feat_dict_gb[k]), reverse=True
            )
            for k in islice(gb_keys_sorted, 10):
                if len(feat_dict_gb[k]) > 0:

                    hint = get_group_by_hint(k, gb_seen, feat_dict_gb[k])
                    # print( k, feat_dict_gb[k], hint)
                    if hint:
                        hints += " - " + hint + "\n"

            # === AGGREGATE HINTS ===
            hints += "\nAggregation Candidates:\n"
            agg_seen = set()
            agg_keys_sorted = sorted(
                feat_dict_aggregate,
                key=lambda k: len(feat_dict_aggregate[k]),
                reverse=True,
            )
            for k in islice(agg_keys_sorted, 10):
                if len(feat_dict_aggregate[k]) > 0:
                    hint = get_aggregate_hint(k, agg_seen, feat_dict_aggregate[k])
                    hint += get_aggregation_function_hint(directory, k)
                    if hint:
                        hints += " - " + hint + "\n"

        # return [hints]

        if hint_source == "v1_kv":
            # print(feat_dict_gb, feat_dict_aggregate)
            hints += "Group By Candidates : \n"
            cnt = 0
            for k in sorted(
                feat_dict_gb, key=lambda k: len(feat_dict_gb[k]), reverse=True
            ):
                cnt += 1
                if cnt > 10:
                    break
                if len(feat_dict_gb[k]) > 0:
                    hint = f" - {k}  " + " { "
                    for ky, v in feat_dict_gb[k].items():
                        hint += f"{ky} : {v} , "
                    hint = hint[:-3] + " }\n"
                    hints += hint

            hints += "Aggregation Candidates : \n"
            cnt = 0
            for k in sorted(
                feat_dict_aggregate,
                key=lambda k: len(feat_dict_aggregate[k]),
                reverse=True,
            ):
                cnt += 1
                if cnt > 10:
                    break
                if len(feat_dict_aggregate[k]) > 0:
                    hint = f" - {k} : " + " { "
                    for ky, v in feat_dict_aggregate[k].items():
                        hint += f"{ky} : {v} , "
                    hint = hint[:-3] + " }"
                    hints += hint
    # print(hints)
    return [hints]
    # return dict(sorted(feat_dict_gb.items(), key=lambda item: len(item[1]), reverse=True)),dict(sorted(feat_dict_aggregate.items(), key=lambda item: len(item[1]), reverse=True))


def get_truncated_aggreggation_features(f, flag, aht, group_by_flag):
    feature_list = {}
    if flag:
        if group_by_flag:
            # [dvr_ub,dvr_lb, leftness_ub,leftness_lb, emptiness_ub,emptiness_lb, peak_frequency_ub, peak_frequency_lb,value_range_ub, value_range_lb]
            if f[1] <= aht[1]:  # low distinct value ratio
                feature_list["Distinct Value Ratio"] = round(f[1], 2)
            if (1 - f[4]) >= aht[2]:  # high leftness
                feature_list["Leftness"] = round(f[2], 2)
            if f[5] <= aht[5]:  # low emptines
                feature_list["Emptiness"] = round(f[4], 2)
            if f[9] >= aht[6]:  # high peak frequerncy
                feature_list["Peak Frequency"] = round(f[7], 2)
            if (
                f[2] in [0, 1] and f[7] <= aht[9]
            ):  # small value range for group by column
                feature_list["Value Range"] = round(f[5], 2)
            if f[2] in [2]:  # string datatype
                feature_list["datatype"] = "String"

        else:  # aggregation feature
            # [dvr_ub,dvr_lb, leftness_ub,leftness_lb, emptiness_ub,emptiness_lb, peak_frequency_ub, peak_frequency_lb,value_range_ub, value_range_lb]
            # [01, 23, 45, 67, 89]
            # [0.9,0.1,0.9,0.1,0.9,0.1,0.9,0.1,0.9,0.1]
            if f[1] >= aht[0]:  # high distinct value ratio
                feature_list["Distinct Value Ratio"] = round(f[1], 2)
            if f[3] <= aht[3]:  # low leftness
                feature_list["Leftness"] = round(f[2], 2)
            if f[4] >= aht[4]:  # may have high emptines
                feature_list["Emptiness"] = round(f[4], 2)
            if f[7] <= aht[7]:  # may have low peak frequerncy
                feature_list["Peak Frequency"] = round(f[7], 2)
            if (
                f[2] in [0, 1] and f[6] >= aht[8]
            ):  # large value range for group by column
                feature_list["Value Range"] = round(f[5], 2)
            if f[2] in [0, 1]:
                feature_list["datatype"] = "Numerical"
    # print(feature_list)
    return feature_list


def check_feature_group_by(f, flag, aht):
    if flag:
        # distinct_value_ratio
        if f[1] < aht[0]:
            return False
        # leftness
        if f[3] < aht[1]:
            return False
        # emptiness
        if f[4] > aht[2]:
            return False
        # peak frequency
        if f[7] < aht[3]:
            return False
