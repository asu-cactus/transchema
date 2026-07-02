# todo
# check datetime datatype
# in integer group by , leftness seems like a must

from model.join import data as jd
from model.aggregation import data as ad
import pandas as pd
import os
import json
import numpy as np
from itertools import combinations
from parameters import hints_v3_truncates as trun


column_level_attributes = {}
# column_level_attributes["A"] = {"dvr" : value, "type" : value, "l" : value, "s" : value, "j1" : value, j2 : value, j3 : value, j5 : value, j6 : value)
pair_level_attributes = {}
# pair_level_attributes["A<->B"] = {"js" : value, "jc" : value, "vro" : value, "jf" : value, "j1" : value, j2 : value, j3 : value, j5 : value, j6 : value)
table_level_attributes = {}
# table_level_attributes["A"] = {"r" : value)


def load_tables(directory, source_data_name_list, len_idx_target_idx):
    tables = {}
    for source_data_name in source_data_name_list:

        if source_data_name.startswith("Source"):
            i = source_data_name.split("_")[-1]
            filename = f"test_{i}"
        else:
            filename = source_data_name

        df = pd.read_csv(f"{directory}/length{len_idx_target_idx}/{filename}.csv")
        tables[source_data_name] = df.drop(df.columns[0], axis=1)

    return tables


def get_distinct_value_ratio(T1_C1, k):
    if k in column_level_attributes and "dvr" in column_level_attributes[k]:
        return column_level_attributes[k]["dvr"]

    else:
        if k not in column_level_attributes:
            column_level_attributes[k] = {}
        # calculate the distinct value ratio
        dvr = jd.distinct_value_ratio(T1_C1, len(T1_C1))
        column_level_attributes[k]["dvr"] = dvr
        return dvr
    return 0


def get_jaccard_similarity(col1, col2, t1, t2, c1, c2):
    k = f"{t1}.{c1}<->{t2}.{c2}"
    if k in pair_level_attributes and "js" in pair_level_attributes[k]:
        return pair_level_attributes[k]["js"]

    else:
        if k not in column_level_attributes:
            column_level_attributes[k] = {}
        # calculate the jaccard similarity
        js = jd.jaccard_similarity(col1, col2)
        pair_level_attributes[k]["js"] = js
        return js


def get_jaccard_containment(col1, col2, t1, t2, c1, c2):
    k = f"{t1}.{c1}<->{t2}.{c2}"
    if k in pair_level_attributes and "jc" in pair_level_attributes[k]:
        return pair_level_attributes[k]["jc"]

    else:
        if k not in pair_level_attributes:
            pair_level_attributes[k] = {}
        # calculate the jaccard containment
        jc = jd.jaccard_containment(col1, col2)
        # print("Jaccard Containment : ",c1,c2,jc)
        pair_level_attributes[k]["jc"] = jc
        return jc


def match(col1, col2, t1, t2, c1, c2):
    # check if the column is already matched

    k = f"{t1}.{c1}<->{t2}.{c2}"
    k1 = f"{t1}.{c1}"
    k2 = f"{t2}.{c2}"
    if k in pair_level_attributes and "match" in pair_level_attributes[k]:
        return True

    else:
        if k not in pair_level_attributes:
            pair_level_attributes[k] = {}
        # calculate the match
        if (
            get_jaccard_similarity(col1, col2, t1, t2, c1, c2) >= trun["t1"]
            or get_jaccard_containment(col1, col2, t1, t2, c1, c2) >= trun["t2"]
            or get_value_range_overlap(col1, col2, t1, t2, c1, c2) >= trun["t3"]
            or (
                get_type(col1, k1) == get_type(col2, k2)
                and get_jaccard_containment(col2, col1, t2, t1, c2, c1) >= trun["t2"]
            )
        ):

            pair_level_attributes[k]["match"] = True
            return True

    return False


def get_type(T1_C1, k):
    if k in column_level_attributes and "type" in column_level_attributes[k]:
        return column_level_attributes[k]["type"]

    else:
        if k not in column_level_attributes:
            column_level_attributes[k] = {}
        # calculate the type
        t = jd.column_type(T1_C1)
        column_level_attributes[k]["type"] = t
        return t


def get_leftness(col, t, c, pos, total_columns):
    k = f"{t}.{c}"
    if k in column_level_attributes and "l" in column_level_attributes[k]:
        return column_level_attributes[k]["l"]

    else:
        if k not in column_level_attributes:
            column_level_attributes[k] = {}
        # calculate the leftness
        pos, leftness = jd.leftness(pos, total_columns)
        column_level_attributes[k]["l"] = leftness
        return leftness


def get_average_leftness(
    col1, col2, t1, t2, c1, c2, pos1, pos2, total_columns1, total_columns2
):
    k = f"{t1}.{c1}<->{t2}.{c2}"
    if k in pair_level_attributes and "al" in pair_level_attributes[k]:
        return pair_level_attributes[k]["al"]

    else:
        if k not in pair_level_attributes:
            pair_level_attributes[k] = {}
        # calculate the average leftness
        al = (
            get_leftness(col1, t1, c1, pos1, total_columns1)
            + get_leftness(col2, t2, c2, pos2, total_columns2)
        ) / 2
        pair_level_attributes[k]["al"] = al
        return al


def get_sortedness(col, t, c):
    k = f"{t}.{c}"
    if k in column_level_attributes and "s" in column_level_attributes[k]:
        return column_level_attributes[k]["s"]

    else:
        if k not in column_level_attributes:
            column_level_attributes[k] = {}
        # calculate the sortedness
        s = jd.is_sorted(col)
        column_level_attributes[k]["s"] = s
        return s


def get_missing_value_ratio(table, t):
    if t in table_level_attributes and "mvr" in table_level_attributes[t]:
        return table_level_attributes[t]["mvr"]

    else:
        if t not in table_level_attributes:
            table_level_attributes[t] = {}
        # calculate the missing value ratio
        mvr = table.isna().sum().sum() / (table.shape[0] * table.shape[1])
        table_level_attributes[t]["mvr"] = mvr
        return mvr


def get_emptiness(col, k):
    if k in column_level_attributes and "e" in column_level_attributes[k]:
        return column_level_attributes[k]["e"]

    else:
        if k not in column_level_attributes:
            column_level_attributes[k] = {}
        # calculate the emptiness
        e = ad.emptiness(col)
        column_level_attributes[k]["e"] = e
        return e


def get_peak_frequency(col, k):
    if k in column_level_attributes and "pf" in column_level_attributes[k]:
        return column_level_attributes[k]["pf"]

    else:
        if k not in column_level_attributes:
            column_level_attributes[k] = {}
        # calculate the peak frequency
        a, b = ad.peak_frequency(col)
        column_level_attributes[k]["pf"] = b
        return b


def get_value_range(col, k):
    if k in column_level_attributes and "vr" in column_level_attributes[k]:
        return column_level_attributes[k]["vr"]

    else:
        if k not in column_level_attributes:
            column_level_attributes[k] = {}
        # calculate the value range
        vr = ad.value_range(col)
        column_level_attributes[k]["vr"] = vr
        return vr


def get_column_equivalence(table):
    supporting_sets = {}

    for col in table.columns:
        support = []
        for other_col in table.columns:
            if (table[col] == table[other_col]).all():
                support.append(other_col)
        supporting_sets[col] = support

    # Find the column with the largest supporting set
    max_col = max(supporting_sets, key=lambda k: len(supporting_sets[k]))
    max_supporting_set = supporting_sets[max_col]
    return max_supporting_set


def get_value_range_overlap(col1, col2, t1, t2, c1, c2):
    k = f"{t1}.{c1}<->{t2}.{c2}"
    if k in pair_level_attributes and "vro" in pair_level_attributes[k]:
        return pair_level_attributes[k]["vro"]

    else:
        if k not in pair_level_attributes:
            pair_level_attributes[k] = {}
        # calculate the value range overlap
        # if(c1 == "COD_IDCONTRA" and c2 == "COD_IDCONTRA") :
        #     print("Calculating value range overlap for COD_IDCONTRA")
        vro = jd.value_range_overlap(col1, col2)
        pair_level_attributes[k]["vro"] = vro
        return vro


######################## composite functions ############################
def key(col, t, c):
    k = f"{t}.{c}"
    if k in column_level_attributes and "key" in column_level_attributes[k]:
        return True

    if get_type(col, k) in ["int64", "object", "datetime"]:

        if get_distinct_value_ratio(col, k) >= 0.95:
            column_level_attributes[k]["key"] = True
            return True
    return False


def foreign_key(col1, col2, t1, t2, c1, c2):
    # get T1 from T1_C1
    k = f"{t2}.{c2}<->{t1}"
    if k in pair_level_attributes and "fk" in pair_level_attributes[k]:
        return True

    else:
        # calculate the foreign_key
        if k not in pair_level_attributes:
            pair_level_attributes[k] = {}
        if key(col1, t1, c1) and match(col1, col2, t1, t2, c1, c2):
            pair_level_attributes[k]["fk"] = True
            return True

    return False


def join_check_1(col1, col2, t1, t2, c1, c2):
    # get T1 from T1_C1
    k = f"{t2}.{c2}<->{t1}.{c1}"
    k1 = f"{t1}.{c1}"
    k2 = f"{t2}.{c2}"
    if k in pair_level_attributes and "j1" in pair_level_attributes[k]:
        return True

    else:
        # calculate the foreign_key
        if k not in pair_level_attributes:
            pair_level_attributes[k] = {}
        if (
            get_type(col1, k1) == get_type(col2, k2)
            and len(col1) > trun["t4"]
            and len(col2) > trun["t4"]
            and match(col1, col2, t1, t2, c1, c2)
        ):
            pair_level_attributes[k]["j1"] = True
            return True

    return False


def join_check_2(col1, col2, t1, t2, c1, c2):
    # get T1 from T1_C1
    k = f"{t2}.{c2}<->{t1}.{c1}"
    k1 = f"{t1}.{c1}"
    k2 = f"{t2}.{c2}"
    if k not in pair_level_attributes:
        pair_level_attributes[k] = {}
    if foreign_key(col1, col2, t1, t2, c1, c2) and join_check_1(
        col1, col2, t1, t2, c1, c2
    ):
        return True
    return False


def join_check_3(
    col1, col2, t1, t2, c1, c2, pos1, pos2, total_columns1, total_columns2
):
    # get T1 from T1_C1
    k = f"{t2}.{c2}<->{t1}.{c1}"
    k1 = f"{t1}.{c1}"
    k2 = f"{t2}.{c2}"

    # calculate the foreign_key
    if k not in pair_level_attributes:
        pair_level_attributes[k] = {}
    if get_average_leftness(
        col1, col2, t1, t2, c1, c2, pos1, pos2, total_columns1, total_columns2
    ) <= trun["t13"] and join_check_1(col1, col2, t1, t2, c1, c2):
        return True

    return False


def join_check_4(col1, col2, t1, t2, c1, c2):
    # get T1 from T1_C1
    k = f"{t2}.{c2}<->{t1}.{c1}"
    k1 = f"{t1}.{c1}"
    k2 = f"{t2}.{c2}"

    # calculate the foreign_key
    if k not in pair_level_attributes:
        pair_level_attributes[k] = {}
    if (get_sortedness(col1, t1, c1) or get_sortedness(col2, t2, c2)) and join_check_1(
        col1, col2, t1, t2, c1, c2
    ):
        return True

    return False


def join_check_5(
    col1, col2, t1, t2, c1, c2, pos1, pos2, total_columns1, total_columns2
):
    # get T1 from T1_C1
    k = f"{t2}.{c2}<->{t1}.{c1}"
    k1 = f"{t1}.{c1}"
    k2 = f"{t2}.{c2}"

    # calculate the foreign_key
    if k not in pair_level_attributes:
        pair_level_attributes[k] = {}
    if (
        get_average_leftness(
            col1, col2, t1, t2, c1, c2, pos1, pos2, total_columns1, total_columns2
        )
        <= trun["t13"]
        and (get_sortedness(col1, t1, c1) or get_sortedness(col2, t2, c2))
        and join_check_1(col1, col2, t1, t2, c1, c2)
    ):
        return True

    return False


def group_by_check1(col, t, c, pos, total_columns):
    # get T1 from T1_C1
    k = f"{t}.{c}"
    if k in column_level_attributes and "gb1" in column_level_attributes[k]:
        return True

    else:
        # calculate the foreign_key
        if k not in column_level_attributes:
            column_level_attributes[k] = {}
        if (
            get_type(col, k) in ["object", "bool", "datetime"]
            and get_peak_frequency(col, k) > trun["t10"]
            and get_emptiness(col, k) < trun["t9"]
            and get_distinct_value_ratio(col, k) < trun["t8"]
        ):
            column_level_attributes[k]["gb1"] = True
            return True

    return False


def group_by_check2(col, t, c, pos, total_columns):
    # get T1 from T1_C1
    k = f"{t}.{c}"
    if k in column_level_attributes and "gb2" in column_level_attributes[k]:
        return True

    else:
        # calculate the foreign_key
        if k not in column_level_attributes:
            column_level_attributes[k] = {}
        if (
            get_type(col, k) in ["int64"]
            and get_peak_frequency(col, k) > trun["t10"]
            and get_emptiness(col, k) < trun["t9"]
            and get_distinct_value_ratio(col, k) < trun["t8"]
            and get_value_range(col, k) <= trun["t11"]
        ):
            column_level_attributes[k]["gb2"] = True
            return True

    return False


def group_by_check3(col, t, c, pos, total_columns):
    k = f"{t}.{c}"
    if (
        get_type(col, k) in ["object", "bool", "datetime"]
        and get_emptiness(col, k) < trun["t9"]
        and get_distinct_value_ratio(col, k) < trun["t8"]
    ):
        return True

    return False


def group_by_check4(col, t, c, pos, total_columns):
    k = f"{t}.{c}"
    if (
        get_type(col, k) in ["int64"]
        and get_emptiness(col, k) < trun["t9"]
        and get_distinct_value_ratio(col, k) < trun["t8"]
        and get_value_range(col, k) <= trun["t11"]
        and get_leftness(col, t, c, pos, total_columns) < 0.2
    ):
        return True

    return False


def get_group_by_status(col, t, c, pos, total_columns):
    if (
        group_by_check1(col, t, c, pos, total_columns)
        or group_by_check2(col, t, c, pos, total_columns)
        or group_by_check3(col, t, c, pos, total_columns)
        or group_by_check4(col, t, c, pos, total_columns)
    ):
        return True
    return False


def group_by_check5(col, target_column, t, c, pos, total_columns):
    k = f"{t}.{c}"
    if (
        match(col, target_column, t, "target", c, c)
        and get_group_by_status(col, t, c, pos, total_columns)
        and get_distinct_value_ratio(target_column, f"target.{c}")
    ):
        return True
    return False


def group_by_check6(col, target_column, t, c, pos, total_columns):
    k = f"{t}.{c}"
    if (
        match(col, target_column, t, "target", c, c)
        and get_group_by_status(col, t, c, pos, total_columns)
        and key(target_column, "target", c)
    ):
        return True
    return False


def aggregation_check1(col, t, c, pos, total_columns):
    # get T1 from T1_C1
    k = f"{t}.{c}"

    # calculate the foreign_key
    if (
        get_type(col, k) in ["int64", "float64"]
        and get_leftness(col, t, c, pos, total_columns) > trun["t12"]
    ):
        return True

    return False


def aggregation_check2(col, t, c, pos, total_columns):
    k = f"{t}.{c}"

    if (
        get_type(col, k) in ["object", "datetime", "bool"]
        and get_leftness(col, t, c, pos, total_columns) > trun["t12"]
    ):
        return True

    return False


def aggregation_check3(
    col,
    target_column,
    t,
    c,
    pos,
    total_columns,
    target_col_position,
    total_target_columns,
):
    k = f"{t}.{c}"
    if (
        get_type(col, k) == get_type(target_column, f"target.{c}")
        and (get_type(col, k) in ["float64", "int64"])
        and get_average_leftness(
            col,
            target_column,
            t,
            "target",
            c,
            c,
            pos,
            target_col_position,
            total_columns,
            total_target_columns,
        )
        > trun["t12"]
    ):
        return True
    return False


def aggregation_check4(
    col,
    target_column,
    t,
    c,
    pos,
    total_columns,
    target_col_position,
    total_target_columns,
):
    k = f"{t}.{c}"
    if (
        get_type(col, k) != "int64"
        and get_type(target_column, f"target.{c}") == "int64"
        and get_average_leftness(
            col,
            target_column,
            t,
            "target",
            c,
            c,
            pos,
            target_col_position,
            total_columns,
            total_target_columns,
        )
        > trun["t12"]
    ):
        return True
    return False


def aggregation_check5(
    col,
    target_column,
    t,
    c,
    pos,
    total_columns,
    target_col_position,
    total_target_columns,
):
    k = f"{t}.{c}"
    if (
        get_type(col, k) == get_type(target_column, f"target.{c}")
        and (get_type(col, k) in ["float64", "int64"])
        and get_average_leftness(
            col,
            target_column,
            t,
            "target",
            c,
            c,
            pos,
            target_col_position,
            total_columns,
            total_target_columns,
        )
        > trun["t12"]
        and np.mean(target_column) / np.mean(col) > 10
    ):
        return True
    return False


def aggregation_check6(
    col,
    target_column,
    t,
    c,
    pos,
    total_columns,
    target_col_position,
    total_target_columns,
):
    k = f"{t}.{c}"
    if (
        get_type(col, k) == get_type(target_column, f"target.{c}")
        and (get_type(col, k) in ["float64", "int64"])
        and get_average_leftness(
            col,
            target_column,
            t,
            "target",
            c,
            c,
            pos,
            target_col_position,
            total_columns,
            total_target_columns,
        )
        > trun["t12"]
        and np.mean(target_column) / np.mean(col) > 0.5
        and np.mean(target_column) / np.mean(col) < 2
    ):
        return True
    return False


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
    # check for foreign key
    hints = ""
    tables = load_tables(directory, source_data_name_list, len_idx_target_idx)
    target_file = os.path.join(directory, f"length{len_idx_target_idx}", "target.csv")
    target_table = pd.read_csv(target_file, low_memory=False)
    target_table = target_table.drop(target_table.columns[0], axis=1)

    for table_name1, table_name2 in combinations(tables, 2):
        table1 = tables[table_name1]
        table2 = tables[table_name2]
        columns1 = table1.columns
        columns2 = table2.columns
        total_columns1 = len(columns1)
        total_columns2 = len(columns2)

        for col1 in columns1:
            for col2 in columns2:

                # print(f"Checking {table_name1}.{col1} and {table_name2}.{col2}")
                hint = ""

                # Highest severity → lowest
                if join_check_2(
                    table1[col1], table2[col2], table_name1, table_name2, col1, col2
                ):
                    hint = f"It is HIGHLY PROBABLE that {table_name1} JOIN {table_name2} ON {table_name1}.{col1} = {table_name2}.{col2}\n"

                elif join_check_5(
                    table1[col1],
                    table2[col2],
                    table_name1,
                    table_name2,
                    col1,
                    col2,
                    columns1.get_loc(col1),
                    columns2.get_loc(col2),
                    total_columns1,
                    total_columns2,
                ):
                    hint = f"It is HIGHLY POSSIBLE that {table_name1} JOIN {table_name2} ON {table_name1}.{col1} = {table_name2}.{col2}\n"

                # elif join_check_3(table1[col1], table2[col2], table_name1, table_name2, col1, col2, columns1.get_loc(col1), columns2.get_loc(col2), total_columns1, total_columns2):
                #     hint = f"It is probable that {table_name1} JOIN {table_name2} ON {table_name1}.{col1} = {table_name2}.{col2}\n"

                # elif join_check_4(table1[col1], table2[col2], table_name1, table_name2, col1, col2):
                #     hint = f"It is probable that {table_name1} JOIN {table_name2} ON {table_name1}.{col1} = {table_name2}.{col2}\n"

                # elif foreign_key(table1[col1], table2[col2], table_name1, table_name2, col1, col2):
                #     hint = f"It is possible that {table_name1} JOIN {table_name2} ON {table_name1}.{col1} = {table_name2}.{col2}\n"

                # elif join_check_1(table1[col1], table2[col2], table_name1, table_name2, col1, col2):
                #     hint = f"It is possible that {table_name1} JOIN {table_name2} ON {table_name1}.{col1} = {table_name2}.{col2}\n"

                if (
                    join_check_1(
                        table1[col1], table2[col2], table_name1, table_name2, col1, col2
                    )
                    and get_jaccard_containment(
                        table1[col1], table2[col2], table_name1, table_name2, col1, col2
                    )
                    >= trun["t6"]
                    and get_jaccard_containment(
                        table2[col2], table1[col1], table_name2, table_name1, col2, col1
                    )
                    <= trun["t7"]
                    and get_missing_value_ratio(target_table, "target") > trun["t5"]
                ):
                    hint = f"It is possible that {table_name1} LEFT OUTER JOIN {table_name2} ON {table_name1}.{col1} = {table_name2}.{col2}\n"

                if (
                    join_check_1(
                        table1[col1], table2[col2], table_name1, table_name2, col1, col2
                    )
                    and get_jaccard_containment(
                        table2[col2], table1[col1], table_name2, table_name1, col2, col1
                    )
                    >= trun["t6"]
                    and get_jaccard_containment(
                        table1[col1], table2[col2], table_name1, table_name2, col1, col2
                    )
                    <= trun["t7"]
                    and get_missing_value_ratio(target_table, "target") > trun["t5"]
                ):
                    hint = f"It is possible that {table_name1} RIGHT OUTER JOIN {table_name2} ON {table_name1}.{col1} = {table_name2}.{col2}\n"

                if hint:
                    hints += hint
    return [hints]


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
    tables = load_tables(directory, source_data_name_list, len_idx_target_idx)
    target_file = os.path.join(directory, f"length{len_idx_target_idx}", "target.csv")
    target_table = pd.read_csv(target_file)
    target_table = target_table.drop(target_table.columns[0], axis=1)
    target_columns = target_table.columns

    # get group by hints
    hints += "Group by hints:\n"

    for table_name, table in tables.items():
        columns = table.columns
        total_columns = len(columns)
        for pos, col_name in enumerate(columns):

            # only source table based attributes
            if group_by_check1(
                table[col_name], table_name, col_name, pos, total_columns
            ):
                hints += f"It is possible that the previous results are applied with GROUP By {table_name}.{col_name}\n"
            elif group_by_check2(
                table[col_name], table_name, col_name, pos, total_columns
            ):
                hints += f"It is possible that the previous results are applied with GROUP By {table_name}.{col_name}\n"
            elif group_by_check3(
                table[col_name], table_name, col_name, pos, total_columns
            ):
                hints += f"It is possible that the previous results are applied with GROUP By {table_name}.{col_name}\n"
            elif group_by_check4(
                table[col_name], table_name, col_name, pos, total_columns
            ):
                hints += f"It is probable that the previous results are applied with GROUP By {table_name}.{col_name}\n"

            # target table based attributes
            if col_name in target_columns:
                if group_by_check6(
                    table[col_name],
                    target_table[col_name],
                    table_name,
                    col_name,
                    pos,
                    total_columns,
                ):
                    hints += f"It is highly probable that the previous results are applied with GROUP By {table_name}.{col_name}\n"
                elif group_by_check5(
                    table[col_name],
                    target_table[col_name],
                    table_name,
                    col_name,
                    pos,
                    total_columns,
                ):
                    hints += f"It is probable that the previous results are applied with GROUP By {table_name}.{col_name}\n"

    # get aggregation hints
    hints += "Aggregation hints:\n"
    for table_name, table in tables.items():
        columns = table.columns
        total_columns = len(columns)
        for pos, col_name in enumerate(columns):

            # print(col_name, table[col_name].dtype, get_leftness(table[col_name],table_name,col_name,pos,total_columns))

            # Initialize hint
            hint = ""

            # Step 1: Target-based aggregation hints (high confidence)
            for target_col in target_columns:
                try:
                    if col_name.lower() in target_col.lower():
                        target_col_position = target_columns.get_loc(target_col)

                        if aggregation_check5(
                            table[col_name],
                            target_table[target_col],
                            table_name,
                            col_name,
                            pos,
                            total_columns,
                            target_col_position,
                            len(target_columns),
                        ):
                            hint = f"It is highly possible that SUM({table_name}.{col_name}) exists in the transformation logic.\n"
                            break
                        elif aggregation_check4(
                            table[col_name],
                            target_table[target_col],
                            table_name,
                            col_name,
                            pos,
                            total_columns,
                            target_col_position,
                            len(target_columns),
                        ):
                            hint = f"It is highly possible that COUNT({table_name}.{col_name}) exists in the transformation logic.\n"
                            break
                        elif aggregation_check6(
                            table[col_name],
                            target_table[target_col],
                            table_name,
                            col_name,
                            pos,
                            total_columns,
                            target_col_position,
                            len(target_columns),
                        ):
                            hint = f"It is highly possible that AGG({table_name}.{col_name}) exists in the transformation logic, where agg could be AVG, MAX, MIN.\n"
                            break
                        elif aggregation_check3(
                            table[col_name],
                            target_table[target_col],
                            table_name,
                            col_name,
                            pos,
                            total_columns,
                            target_col_position,
                            len(target_columns),
                        ):
                            hint = f"It is highly possible that AGG({table_name}.{col_name}) exists in the transformation logic, where agg could be SUM, AVG, MAX, MIN, COUNT.\n"
                            break
                except:
                    pass

            # Step 2: Source-based aggregation hints (fallback if no target match)
            if not hint:
                try:
                    if aggregation_check1(
                        table[col_name], table_name, col_name, pos, total_columns
                    ):
                        hint = f"It is possible that AGG({table_name}.{col_name}) exists in the transformation logic, where agg could be SUM, AVG, MAX, MIN, COUNT.\n"
                    elif aggregation_check2(
                        table[col_name], table_name, col_name, pos, total_columns
                    ):
                        hint = f"It is possible that COUNT({table_name}.{col_name}) exists in the transformation logic.\n"
                except:
                    pass

            # Append hint if generated
            if hint:
                hints += hint

        # break  # Stop after the first match
    # column equivalence check
    column_set = get_column_equivalence(target_table)
    if len(column_set) > 3:
        hints += (
            f"aggregate {', '.join(column_set)}, by counting them if they equal to each other: "
            + ", ".join([f"Count(Target.{col})" for col in column_set])
            + "\n"
        )

    return [hints]


def get_groupby_hint_columns(
    source_data_name_list,
    directory,
    len_idx_target_idx,
):
    """Return an ordered list of 'table.col' strings that pass group-by checks.

    Runs the same statistical checks as get_groupby_aggregate_hints but
    returns column identifiers directly (not a text blob) so callers can
    build a structured GROUP_BY candidate without text parsing.

    Columns are ordered by confidence tier so higher-confidence candidates
    appear first in the GROUP_BY column list:
      Tier 1 (highest): check6 or check5 — target-column-matched
      Tier 2:           check1 or check2 — source-based, high confidence
      Tier 3:           check3 or check4 — source-based, lower confidence

    Returns:
        List[str]: e.g. ["Source1_9_0.zipcode", "Source1_9_0.AGI_STUB"]
                   Empty list if no columns qualify or data cannot be loaded.
    """
    try:
        tables = load_tables(directory, source_data_name_list, len_idx_target_idx)
        target_file = os.path.join(directory, f"length{len_idx_target_idx}", "target.csv")
        target_table = pd.read_csv(target_file, low_memory=False)
        target_table = target_table.drop(target_table.columns[0], axis=1)
        target_columns = target_table.columns
    except Exception:
        return []

    tier1, tier2, tier3 = [], [], []
    seen = set()

    for table_name, table in tables.items():
        columns = table.columns
        total_columns = len(columns)
        for pos, col_name in enumerate(columns):
            key = f"{table_name}.{col_name}"
            if key in seen:
                continue
            col = table[col_name]

            # Tier 1: target-matched (highest confidence)
            if col_name in target_columns:
                try:
                    target_col = target_table[col_name]
                    if group_by_check6(col, target_col, table_name, col_name, pos, total_columns):
                        tier1.append(key)
                        seen.add(key)
                        continue
                    if group_by_check5(col, target_col, table_name, col_name, pos, total_columns):
                        tier1.append(key)
                        seen.add(key)
                        continue
                except Exception:
                    pass

            # Tier 2: source-based, high confidence
            try:
                if (
                    group_by_check1(col, table_name, col_name, pos, total_columns)
                    or group_by_check2(col, table_name, col_name, pos, total_columns)
                ):
                    tier2.append(key)
                    seen.add(key)
                    continue
            except Exception:
                pass

            # Tier 3: source-based, lower confidence
            try:
                if (
                    group_by_check3(col, table_name, col_name, pos, total_columns)
                    or group_by_check4(col, table_name, col_name, pos, total_columns)
                ):
                    tier3.append(key)
                    seen.add(key)
            except Exception:
                pass

    return tier1 + tier2 + tier3


def get_union_hints(
    hint_source,
    file_count,
    source_data_name_list,
    source_data_schema_list,
    directory,
    len_idx_target_idx,
):
    hints = ""
    tables = load_tables(directory, source_data_name_list, len_idx_target_idx)
    target_file = os.path.join(directory, f"length{len_idx_target_idx}", "target.csv")
    target_table = pd.read_csv(target_file)
    target_table = target_table.drop(target_table.columns[0], axis=1)
    target_columns = target_table.columns

    # get union hints
    # match schema with target
    union_table_set = []
    for table in tables:
        cols = set(tables[table].columns)
        intersection = cols.intersection(target_columns)
        if intersection:
            coverage = len(intersection) / len(target_columns)
            if coverage > 0.8:
                union_table_set.append(table)

    hints += f"It is highly probable that {' ,'.join(union_table_set)} should be unioned together to form the target table.\n"

    for table_name1, table_name2 in combinations(tables, 2):
        table1 = tables[table_name1]
        table2 = tables[table_name2]
        columns1 = table1.columns
        columns2 = table2.columns
        total_columns1 = len(columns1)
        total_columns2 = len(columns2)

        for col1 in columns1:
            for col2 in columns2:
                if (
                    match(
                        table1[col1], table2[col2], table_name1, table_name2, col1, col2
                    )
                    and get_value_range_overlap(
                        table1[col1], table2[col2], table_name1, table_name2, col1, col2
                    )
                    < 0.2
                ):
                    hints += f"It is possible that {table1}.{col1} and {table2}.{col2} are unioned in the transformation\n"

    return [hints]


if __name__ == "__main__":
    operator_type = "join"

    if operator_type == "join":
        pass
