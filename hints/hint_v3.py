# todo
# check datetime datatype
# in integer group by , leftness seems like a must

from model.join import data as jd
from model.aggregation import data as ad
import pandas as pd
import os
import json
import re
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


def _normalize_col_name(name):
    return re.sub(r"[^a-z0-9]+", "", str(name).lower())


def _tokenize_col_name(name):
    return {t for t in re.split(r"[^a-zA-Z0-9]+", str(name)) if t}


def name_score(c1, c2):
    # 1.0 exact normalized match; else token-jaccard partial credit; else 0.0
    if _normalize_col_name(c1) == _normalize_col_name(c2):
        return 1.0
    t1, t2 = _tokenize_col_name(c1), _tokenize_col_name(c2)
    if not t1 or not t2:
        return 0.0
    inter = t1 & t2
    if not inter:
        return 0.0
    return len(inter) / len(t1 | t2)


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


def evidence_score(col1, col2, t1, t2, c1, c2):
    # continuous version of match()'s own logic: the strongest of the same
    # signals match() thresholds, instead of an OR-of-thresholds boolean
    return max(
        get_jaccard_similarity(col1, col2, t1, t2, c1, c2),
        get_jaccard_containment(col1, col2, t1, t2, c1, c2),
        get_jaccard_containment(col2, col1, t2, t1, c2, c1),
        get_value_range_overlap(col1, col2, t1, t2, c1, c2),
    )


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
        # SUM threshold: target/source mean ratio. A true SUM produces a ratio
        # equal to the average GROUP BY group size, so the old > 10 cutoff
        # silently missed every case with fewer than ~10 rows per group — e.g.
        # length1_9 (6 rows per zipcode, ratio 6.02) never got a SUM hint.
        and np.mean(target_column) / np.mean(col) > 5
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


######################## AGGREGATE reranking ############################
def aggregation_condition_bucket(source_col, target_col):
    """Which aggregation function(s) the source_col -> target_col dtype/
    magnitude relationship is consistent with. Reuses aggregation_check3-6's
    dtype/ratio logic, stripped of the leftness requirement, evaluated as
    independent conditions rather than a first-hit-wins cascade. Returns a
    set of function names ({"SUM"}, {"COUNT"}, {"AVG","MIN","MAX"}, the
    5-way generic catch-all, or an empty set if nothing can be evaluated).
    """
    source_type = str(source_col.dtype)
    target_type = str(target_col.dtype)

    # COUNT: dtype flips to pure integer target from a non-int64 source.
    # Near-mutually-exclusive with the ratio buckets below, which require
    # identical source/target dtype.
    if source_type != "int64" and target_type == "int64":
        return {"COUNT"}

    if source_type == target_type and source_type in ("int64", "float64"):
        try:
            source_mean = source_col.mean()
            target_mean = target_col.mean()
            if not source_mean:
                return set()
            ratio = target_mean / source_mean
        except Exception:
            return set()
        # Matches aggregation_check5's SUM threshold. A true SUM produces a
        # ratio equal to the average GROUP BY group size, so the old > 10
        # cutoff missed every case with fewer than ~10 rows per group and
        # dropped them into the 5-way catch-all below, where SUM tied with
        # MAX/MIN/AVG/COUNT at 0.2 each and the reranker could not
        # discriminate (length1_9: ratio 6.02 for every target column).
        if ratio > 5:
            return {"SUM"}
        if 0.5 < ratio < 2:
            return {"AVG", "MIN", "MAX"}
        # Ambiguous middle (2 <= ratio <= 5) — generic catch-all. COUNT is
        # deliberately excluded: this branch is only reachable when source and
        # target share the same numeric dtype, whereas COUNT's signature is a
        # dtype FLIP to whole numbers, already returned as {"COUNT"} above.
        # Including it here only diluted every other function's score.
        return {"SUM", "AVG", "MIN", "MAX"}

    return set()


def aggregation_condition_score(bucket, func):
    # 1/|bucket| when func is in the matched bucket, else 0 — a column with
    # exactly one clean answer scores full value; ambiguity reduces it.
    if not bucket or func not in bucket:
        return 0.0
    return 1.0 / len(bucket)


def _distribution_reason(source_col, target_col, bucket):
    """Human-readable justification for a bucket, phrased in terms of the
    distributions it was derived from."""
    try:
        ratio = target_col.mean() / source_col.mean()
    except Exception:
        ratio = None

    if bucket == {"COUNT"}:
        return (
            f"source is {source_col.dtype} but target is {target_col.dtype} — a "
            "dtype flip to whole numbers is the signature of a COUNT"
        )
    if bucket == {"SUM"}:
        return (
            f"target average is {ratio:.1f}x the source average, i.e. each target "
            "row aggregates several source rows by addition"
        )
    if bucket == {"AVG", "MIN", "MAX"}:
        return (
            f"target average is close to the source average (ratio {ratio:.2f}), so "
            "the value is representative of the group rather than accumulated"
        )
    if ratio is not None:
        return f"ratio {ratio:.2f} is not decisive — any of these remain possible"
    return "distributions could not be compared"


def get_aggregation_distribution_hints(source_df, target_df, group_by_cols=None):
    """Per-target-column aggregation evidence derived PURELY from the value
    distributions — deliberately no leftness/position filter.

    aggregation_check3-6 (used by get_groupby_aggregate_hints) gate every
    suggestion behind get_average_leftness(...) > trun["t12"] (0.7), which
    only fires for columns near the RIGHT edge of a wide table. On length1_9
    the three target columns sit near the left of a 77-column source
    (avg leftness 0.28/0.41/0.58), so all three were silently skipped and no
    aggregation hint was produced at all. When a source column is already
    known to correspond to a target column, its position carries no
    information about which aggregation applies — only its distribution does.

    Parameters
    ----------
    source_df       : the table the aggregation will be applied to (the
                      intermediate result at this point in the pipeline).
    target_df       : the target table.
    group_by_cols   : bare column names already committed as GROUP BY keys;
                      they need no aggregation and are skipped.

    Returns a rendered hint block, or "" when there is nothing to report.
    """
    group_by_cols = {c.split(".")[-1] for c in (group_by_cols or [])}
    lines = []

    for col in target_df.columns:
        if col in group_by_cols or col not in source_df.columns:
            continue
        s_col, t_col = source_df[col], target_df[col]
        if not (
            pd.api.types.is_numeric_dtype(s_col)
            and pd.api.types.is_numeric_dtype(t_col)
        ):
            continue
        try:
            bucket = aggregation_condition_bucket(s_col, t_col)
            if not bucket:
                continue
            suggestion = " or ".join(sorted(bucket))
            confidence = "most likely" if len(bucket) == 1 else "possible"
            lines.append(
                f"  {col}\n"
                f"      source : min={s_col.min():<14.10g} max={s_col.max():<14.10g} "
                f"avg={s_col.mean():<14.10g} sum={s_col.sum():.10g}\n"
                f"      target : min={t_col.min():<14.10g} max={t_col.max():<14.10g} "
                f"avg={t_col.mean():<14.10g} sum={t_col.sum():.10g}\n"
                f"      --> {suggestion}  ({confidence}: "
                f"{_distribution_reason(s_col, t_col, bucket)})"
            )
        except Exception:
            continue

    # ── Target columns with NO same-named source column ───────────────────
    # The loop above skips these (`col not in source_df.columns`), which means the
    # columns MOST likely to need a multi-column expression got no evidence at all:
    # a target with no name match is precisely the one that may be a combination of
    # several source columns. Report magnitude evidence for them so the choice is
    # driven by the data rather than left entirely to name guessing.
    unmatched = []
    try:
        for col in target_df.columns:
            if col in group_by_cols or col in source_df.columns:
                continue
            t_col = target_df[col]
            if not pd.api.types.is_numeric_dtype(t_col):
                continue
            unmatched.append(
                f"  {col}  (no source column of this name)\n"
                f"      target : min={t_col.min():<14.10g} max={t_col.max():<14.10g} "
                f"avg={t_col.mean():<14.10g}"
            )
    except Exception:
        unmatched = []

    if not lines and not unmatched:
        return ""

    unmatched_block = ""
    if unmatched:
        unmatched_block = (
            "\n\nTARGET COLUMNS WITH NO SAME-NAMED SOURCE COLUMN\n"
            "Each must be produced from the source columns -- possibly from one, "
            "possibly\nfrom an expression over several:\n\n"
            + "\n\n".join(unmatched)
        )

    if not lines:
        return (
            "══════════════════════════════════════════════════════\n"
            "AGGREGATION EVIDENCE FROM THE DATA (per target column)\n"
            "══════════════════════════════════════════════════════"
            + unmatched_block + "\n\n"
        )

    return (
        "══════════════════════════════════════════════════════\n"
        "AGGREGATION EVIDENCE FROM THE DATA (per target column)\n"
        "══════════════════════════════════════════════════════\n"
        "Value distributions of each target column, compared against the same\n"
        "column in the source data you are aggregating:\n\n"
        + "\n\n".join(lines)
        + "\n\nPrefer the suggested function for each column. It is derived from the\n"
        "actual numbers, so trust it over what the column NAME suggests — a column\n"
        "that looks like a category, code or bracket can still require a SUM.\n"
        "Note the source is a sample, so treat the magnitudes as indicative of the\n"
        "relationship, not as exact totals to reproduce.\n"
        + unmatched_block + "\n\n"
    )


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


def necessity(new_columns, current_schema, target_columns):
    # fraction of the still-missing target columns that new_columns would supply
    missing = set(target_columns) - set(current_schema)
    denom = max(len(missing), 1)
    return len(set(new_columns) & missing) / denom


def compute_join_static_candidates(source_data_name_list, directory, len_idx_target_idx):
    """JOIN analog of get_groupby_hint_columns(): gate every pairwise column
    combination across all source-table pairs via join_check_1, score
    survivors' STATIC components (evidence_score + name_score — necessity is
    per-search-state and resolved elsewhere, not here). Returns {} on load
    failure."""
    try:
        tables = load_tables(directory, source_data_name_list, len_idx_target_idx)
        target_file = os.path.join(directory, f"length{len_idx_target_idx}", "target.csv")
        target_table = pd.read_csv(target_file, low_memory=False)
        target_table = target_table.drop(target_table.columns[0], axis=1)
    except Exception:
        return {}

    target_columns = list(target_table.columns)
    source_columns = {tname: list(t.columns) for tname, t in tables.items()}

    candidates = []
    for table_name1, table_name2 in combinations(tables, 2):
        table1, table2 = tables[table_name1], tables[table_name2]
        for col1 in table1.columns:
            for col2 in table2.columns:
                try:
                    if not join_check_1(
                        table1[col1], table2[col2], table_name1, table_name2, col1, col2
                    ):
                        continue
                    ev = evidence_score(
                        table1[col1], table2[col2], table_name1, table_name2, col1, col2
                    )
                    ns = name_score(col1, col2)
                    candidates.append({
                        "t1": table_name1, "c1": col1,
                        "t2": table_name2, "c2": col2,
                        "evidence": ev, "name_score": ns,
                        "static_score": ev + ns,
                    })
                except Exception:
                    continue

    candidates.sort(key=lambda c: c["static_score"], reverse=True)
    return {
        "candidates": candidates,
        "source_columns": source_columns,
        "target_columns": target_columns,
    }


######################## GROUP BY ranking ############################
def combined_dvr(df, cols):
    # joint distinct-value-ratio of a column set (tuple-of-one collapses to
    # the plain single-column dvr, so single- and multi-column candidates
    # share one code path)
    if len(df) == 0:
        return 0.0
    return len(df[list(cols)].drop_duplicates()) / len(df)


def combined_dvr_delta(intermediate_df, target_df, source_cols, target_cols):
    # "low intermediate dvr, high target dvr" signature, jointly over the set
    return max(
        0.0,
        combined_dvr(target_df, target_cols) - combined_dvr(intermediate_df, source_cols),
    )


def groupby_fd_score(candidate_set, fd_keys):
    # binary membership check against the target's raw FD determinant tuples —
    # same function for every candidate, whether it's FD-sourced or hint-sourced
    return 1.0 if tuple(sorted(candidate_set)) in fd_keys else 0.0


def best_overlapping_table(tables, target_columns):
    # depth-0 fallback: which source table looks most like the target,
    # mirrors get_union_hints' cols.intersection(target_columns) technique
    target_columns = set(target_columns)
    best_table, best_coverage = None, -1.0
    for tname, tdf in tables.items():
        intersection = set(tdf.columns) & target_columns
        coverage = len(intersection) / max(len(target_columns), 1)
        if coverage > best_coverage:
            best_table, best_coverage = tname, coverage
    return best_table


def target_fd_keys(target_table, max_fd_cols=52, timeout=60):
    """Candidate keys of the target table, using the SAME FD engine and
    definition the scorer's fd_f1 uses (eval_score/score.py's _run_fdtool ->
    fdtool.main on the full ground-truth table, columns capped at
    MAX_FD_COLS=52, no row cap, 60s timeout).

    This deliberately does NOT use auto_suggest_llm_util's
    get_multi_column_functional_dependency / quality.quality's
    analyze_functional_dependencies: that path samples 1000 rows (so it is
    non-deterministic and reports keys that are only unique within the
    sample), and its k-level loop returns only the LAST level's FDs — which
    silently discards every single-column determinant found at k=1. On
    length1_9 it reported ('A00100','N1'), which is not a key of the target
    at all, and never reported 'zipcode', which is the target's one true
    minimal key. fdtool.main returns keys=[['zipcode']] there, in 0.02s,
    identically across repeated runs.

    Returns Set[Tuple[str, ...]] (each key's columns sorted), or an empty set
    on timeout/failure.
    """
    import os as _os
    import sys as _sys
    _here = _os.path.dirname(_os.path.abspath(__file__))
    _root = _os.path.dirname(_here)
    for _p in (_root, _os.path.join(_root, "eval_score")):
        if _p not in _sys.path:
            _sys.path.insert(0, _p)
    try:
        from concurrent.futures import ThreadPoolExecutor
        from concurrent.futures import TimeoutError as _FuturesTimeoutError
        import fdtool.fdtool as _fdtool

        with ThreadPoolExecutor(max_workers=1) as _executor:
            _future = _executor.submit(_fdtool.main, target_table.iloc[:, :max_fd_cols])
            try:
                _FDs, _E, _keys = _future.result(timeout=timeout)
            except _FuturesTimeoutError:
                return set()
        return {tuple(sorted(k)) for k in _keys} if _keys else set()
    except Exception:
        return set()


def compute_groupby_static_candidates(source_data_name_list, directory, len_idx_target_idx):
    """STATIC, once-per-case precompute for GROUP BY ranking (mirrors
    compute_join_static_candidates): dtype-gates every source column, records
    leftness and target name-match, and extracts the target table's candidate
    keys via target_fd_keys (the scorer's own fd_f1 FD definition). No
    intermediate table is needed at this stage — necessity's dynamic
    counterpart here, combined_dvr_delta's intermediate side, is resolved
    per-node in nodes.py. Returns {} on load failure."""

    try:
        tables = load_tables(directory, source_data_name_list, len_idx_target_idx)
        target_file = os.path.join(directory, f"length{len_idx_target_idx}", "target.csv")
        target_table = pd.read_csv(target_file, low_memory=False)
        target_table = target_table.drop(target_table.columns[0], axis=1)
    except Exception:
        return {}

    target_columns = list(target_table.columns)
    source_columns = {tname: list(t.columns) for tname, t in tables.items()}
    valid_dtypes = {"object", "bool", "datetime", "int64"}

    individual_columns = []
    for table_name, table in tables.items():
        columns = table.columns
        total_columns = len(columns)
        for pos, col_name in enumerate(columns):
            try:
                col = table[col_name]
                k = f"{table_name}.{col_name}"
                if get_type(col, k) not in valid_dtypes:
                    continue
                leftness = get_leftness(col, table_name, col_name, pos, total_columns)
                matched_target_col = None
                if col_name in target_columns and match(
                    col, target_table[col_name], table_name, "target", col_name, col_name
                ):
                    matched_target_col = col_name
                individual_columns.append({
                    "t": table_name, "c": col_name,
                    "leftness": leftness,
                    "matched_target_col": matched_target_col,
                })
            except Exception:
                continue

    fd_keys = target_fd_keys(target_table)

    return {
        "individual_columns": individual_columns,
        "fd_keys": fd_keys,
        "source_columns": source_columns,
        "target_columns": target_columns,
    }


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
