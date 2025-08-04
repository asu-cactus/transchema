from collections import defaultdict

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from valentine import valentine_match
from valentine.algorithms import Cupid
from model.aggregation.pwr import load_trained_model, predict_columns
import os
from model.join.pwr import predict_join_columns
from quality.quality import (
    analyze_functional_dependencies_1,
    analyze_functional_dependencies,
)
from summary import load_tables


#################### RULE 1 #####################
# UNION HINTS
# RULE WHEN ALL SOURCE TABLES INCLUDE ALL SCHEMAS IN TARGET TABLE
def generate_union_hints(source_dfs, target_df):
    hints = []
    if check_schemas_match(source_dfs, target_df):
        hints.append("Union source tables by target schemas")
    return hints


def check_schemas_match(source_dfs, target_df):
    for df in source_dfs:
        if not all(col in df.columns for col in target_df.columns):
            return False
    return True


#################### RULE 2 #####################
# JOIN HINTS
# RULE WHEN CANDIDATE MATCHING COLUMNS ARE HIGHLY CONFIDENT
def generate_join_hints(source_dfs, mode="heavy", candidate_matching_columns=None):
    hints = []
    if mode == "light":
        # Rule 2: Check for column matches between source tables
        column_matches = check_column_matches(source_dfs)
        if column_matches:
            for match in column_matches:
                hints.append(
                    f"Join table {match[0]} and table {match[1]} on column '{match[2]}'"
                )
    elif mode == "dynamic":
        # Rule 2: Match candidate columns using Cupid algorithm
        matcher = Cupid()
        matches_results = match_candidate_columns(
            source_dfs, candidate_matching_columns, matcher
        )
        for key, matches in matches_results.items():
            table_pair = f"Table {key[0]} and Table {key[1]}"
            for columns_pair, score in matches.items():
                if (
                    score >= 0.90
                ):  # Considering matches with score >= 0.99 as high confidence matches
                    table_1_col, table_2_col = columns_pair[0][1], columns_pair[1][1]
                    if table_1_col == table_2_col:
                        hint = f"Please consider joining {table_pair} on '{table_1_col}' since they have a high matching relationship with a score of {score}."
                    else:
                        hint = f"Please consider joining {table_pair} on '{table_1_col}' and '{table_2_col}' since they have a high matching relationship with a score of {score}."
                    hints.append(hint)
    elif mode == "heavy":
        # Rule 2: Check for column matches between source tables using valentine_match
        matches_results = {}
        matcher = Cupid()
        for i, df1 in enumerate(source_dfs[:-1]):
            for j, df2 in enumerate(source_dfs[i + 1 :], start=i + 1):
                matches = valentine_match(df1, df2, matcher)
                matches_results[(i, j)] = matches

        for key, matches in matches_results.items():
            table_pair = f"Table {key[0]} and Table {key[1]}"
            for columns_pair, score in matches.items():
                if (
                    score >= 0.90
                ):  # Considering matches with score >= 0.99 as high confidence matches
                    table_1_col, table_2_col = columns_pair[0][1], columns_pair[1][1]
                    if table_1_col == table_2_col:
                        hint = f"Please consider joining {table_pair} on '{table_1_col}' since they have a high matching relationship with a score of {score}."
                    else:
                        hint = f"Please consider joining {table_pair} on '{table_1_col}' and '{table_2_col}' since they have a high matching relationship with a score of {score}."
                    hints.append(hint)
    return hints


def check_column_matches(source_dfs):
    matches = []
    for i, df in enumerate(source_dfs):
        for j, df_other in enumerate(source_dfs):
            if i != j:
                common_columns = set(df.columns).intersection(set(df_other.columns))
                for col in common_columns:
                    matches.append((i, j, col))
    return matches


def match_candidate_columns(source_dfs, candidate_matching_columns, matcher):
    matches_results = {}
    for pair in candidate_matching_columns:
        source_1, col_1 = pair[0].split(".")
        source_2, col_2 = pair[1].split(".")
        score = pair[2]
        if score >= 0.90:  # Only consider high confidence matches
            # Exclude 'target' and other non-indexed table names
            if source_1 == "target" or source_2 == "target":
                continue
            table_1_idx = int(source_1.split("_")[1]) if "_" in source_1 else source_1
            table_2_idx = int(source_2.split("_")[1]) if "_" in source_2 else source_2
            df1 = source_dfs[int(table_1_idx)]
            df2 = source_dfs[int(table_2_idx)]
            matches = valentine_match(df1, df2, matcher)
            for (df1_col, df2_col), match_score in matches.items():
                if (
                    df1_col[1] == col_1 and df2_col[1] == col_2
                ) and match_score >= 0.90:
                    if (table_1_idx, table_2_idx) not in matches_results:
                        matches_results[(table_1_idx, table_2_idx)] = {}
                    matches_results[(table_1_idx, table_2_idx)][
                        ((source_1, col_1), (source_2, col_2))
                    ] = match_score
    return matches_results


#################### RULE 3 #####################
# Rule 3: Check for key column overlap
def generate_key_hints(
    tables, source_dfs, target_df, mode="light", candidate_key_columns=None
):
    hints = []
    if mode == "light":
        key_analysis_results = analyze_key_columns(tables, candidate_key_columns)
        for table_name, (FD, Keys) in key_analysis_results.items():
            for Key in Keys:
                hints.append(
                    f"Table {table_name}  has functional dependencies: {FD} and key: {Key}"
                )
    elif mode == "dynamic":
        key_analysis_results = analyze_key_columns(tables, candidate_key_columns)
        for table_name, (FD, Keys) in key_analysis_results.items():
            for Key in Keys:
                hints.append(
                    f"Table {table_name}  has functional dependencies: {FD} and key: {Key}"
                )
    elif mode == "heavy":
        FD, Key = analyze_functional_dependencies(target_df)
        hints.append(f"Target Table has functional dependencies: {FD} and key: {Key}")

    else:
        pass
    return hints


def analyze_key_columns(tables, candidate_key_columns):
    key_analysis_results = defaultdict(dict)

    # Group candidate key columns by table name
    grouped_columns = defaultdict(list)
    for table_name, col_name, score in candidate_key_columns:
        if score >= 0.85:
            grouped_columns[table_name].append(col_name)

    # Analyze functional dependencies for each table with its candidate key columns
    for table_name, columns in grouped_columns.items():
        df = tables[table_name]
        key_analysis_results[table_name] = analyze_functional_dependencies_1(
            df, columns
        )

    return key_analysis_results


#################### RULE 4 #####################
# Rule 4: Check for high uniqueness columns
def generate_high_uniqueness_hints(source_dfs, target_df):
    hints = []
    high_uniqueness, unique_col = check_high_uniqueness_columns(source_dfs, target_df)
    if high_uniqueness and unique_col:
        hints.append(f"Group by '{unique_col}' and aggregate other columns. ")
    elif high_uniqueness:
        hints.append(f"Please use aggregation {unique_col}")
    return hints


def check_high_uniqueness_columns(source_dfs, target_df):
    target_unique_columns = [
        col
        for col in target_df.columns
        if target_df[col].nunique() > len(target_df) * 0.9
    ]

    for df in source_dfs:
        for col in df.columns:
            if col in target_unique_columns and df[col].nunique() <= len(df) * 0.9:
                return True, col
            if df[col].nunique() < len(df) * 0.03:
                return True, col
    return False, None


#################### RULE 5 #####################
# Rule 5:
def check_null_percentage(source_dfs, target_df):
    hints = []
    if check_null_percentage(source_dfs, target_df):
        hints.append("Please remove the rows with NULL values in the target table.")
    return hints


def generate_transformation_hints(
    tables,
    source_dfs,
    target_df,
    mode="light",
    candidate_matching_columns=None,
    candidate_key_columns=None,
    type="join",
):

    hints = []

    if type == "join":
        hints.extend(
            generate_join_hints(
                source_dfs,
                mode=mode,
                candidate_matching_columns=candidate_matching_columns,
            )
        )
        hints.extend(
            generate_key_hints(
                tables,
                source_dfs,
                target_df,
                mode=mode,
                candidate_key_columns=candidate_key_columns,
            )
        )

    elif type == "group_by_aggregate":
        hints.extend(
            generate_key_hints(
                tables,
                source_dfs,
                target_df,
                mode=mode,
                candidate_key_columns=candidate_key_columns,
            )
        )
        hints.extend(generate_high_uniqueness_hints(source_dfs, target_df))

    elif type == "union":
        hints.extend(generate_union_hints(source_dfs, target_df))

    elif type == "get_next_operator":
        pass
    elif type == "python_script":
        hints.extend(check_null_percentage(source_dfs, target_df))
        pass
    else:
        pass

    return ["\n".join(hints)]


if __name__ == "__main__":
    tables = load_tables("model/aggregation/data_test")
    # Load the models
    join_model = load_trained_model("model/join/join_model.json")
    key_model = load_trained_model("model/aggregation/key_model.json")

    # Predict join column pairs
    join_candidates = predict_join_columns(tables, join_model)
    candidate_matching_columns = [
        (f"{t1}.{c1}", f"{t2}.{c2}", s) for (t1, c1), (t2, c2), s in join_candidates
    ]

    # Predict key columns for the target table
    target_table_name = "target"
    target_df = tables[target_table_name]
    # Fit LabelEncoder on all possible data types
    all_data_types = ["int64", "float64", "object"]  # Add more types if needed
    label_encoder = LabelEncoder()
    label_encoder.fit(all_data_types)
    # Predict key columns for all tables
    all_key_candidates = []
    key_candidates = predict_columns(tables, key_model, label_encoder)
    all_key_candidates.extend(key_candidates)

    # print(candidate_matching_columns,'\n\n',all_key_candidates)

    # Generate transformation hints
    source_dfs = [tables[table] for table in tables if table != target_table_name]
    hints = generate_transformation_hints(
        tables,
        source_dfs,
        target_df,
        mode="dynamic",
        candidate_matching_columns=candidate_matching_columns,
        candidate_key_columns=key_candidates,
        type="join",
    )
    # print(hints)
