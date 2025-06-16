import os
import re
import pandas as pd
from collections import defaultdict
from typing import List, Tuple
from validation.hard_match import compare_columns


def avg_tup_(list_tup):
    print("_________________________")
    print(f"averaging {list_tup}")
    avg_cost = 0
    avg_lat = 0
    avg_acc = 0
    avg_score = 0
    for tup in list_tup:
        avg_cost += tup[3]
        avg_lat += tup[4]
        avg_acc += tup[2]
        avg_score += tup[5]
    avg_cost = avg_cost / len(list_tup)
    avg_lat = avg_lat / len(list_tup)
    avg_acc = avg_acc / len(list_tup)
    avg_score = avg_score / len(list_tup)
    # here
    avg = (list_tup[0][0], list_tup[0][1], avg_acc, avg_cost, avg_lat, avg_score)
    return avg


def normalize_column(col: str) -> str:
    """Normalize a column name: lowercase and remove non-alphanumerics."""
    return re.sub(r"[^a-zA-Z0-9]", "", col.strip().lower())


def extract_tokens(col: str) -> List[str]:
    """Tokenize a column name based on delimiters and camel case."""
    col = col.strip().lower()
    col = re.sub(r"([a-z])([A-Z])", r"\1_\2", col)  # camelCase → snake_case
    tokens = re.split(r"[ _\-]+", col)
    return [t for t in tokens if t]


def are_schemas_similar(schema1: List[str], schema2: List[str]) -> bool:
    """Determine if two schemas are similar based on token overlap."""
    if len(schema1) != len(schema2):
        return False

    used = set()
    for col1 in schema1:
        tokens1 = set(extract_tokens(col1))
        found = False
        for i, col2 in enumerate(schema2):
            if i in used:
                continue
            tokens2 = set(extract_tokens(col2))
            if tokens1 & tokens2:
                used.add(i)
                found = True
                break
        if not found:
            return False
    return True


def are_tables_value_similar(
    df1: pd.DataFrame, df2: pd.DataFrame, threshold=0.9
) -> bool:
    """Compare tables column-wise for value similarity with flexible column mapping."""
    if df1.shape != df2.shape:
        return False

    used_cols_df2 = set()
    matched_count = 0

    for col1 in df1.columns:
        col1_tokens = set(extract_tokens(col1))
        best_match = None

        for col2 in df2.columns:
            if col2 in used_cols_df2:
                continue
            col2_tokens = set(extract_tokens(col2))

            if col1_tokens & col2_tokens:
                col_sim = compare_columns(df1[col1].tolist(), df2[col2].tolist())
                if col_sim >= threshold:
                    best_match = col2
                    break

        if best_match:
            used_cols_df2.add(best_match)
            matched_count += 1
        else:
            return False

    return matched_count == df1.shape[1]


def refine_by_value_similarity(
    schema_group: List[Tuple[int, pd.DataFrame]], threshold=0.9
):
    """Split a schema-similar group into subgroups by value similarity."""
    subgroups = []

    for i, df in schema_group:
        matched = False
        for group in subgroups:
            rep_i, rep_df = group[0]
            if are_tables_value_similar(rep_df, df, threshold=threshold):
                group.append((i, df))
                matched = True
                break
        if not matched:
            subgroups.append([(i, df)])
    return subgroups


def analyze_results(args, results, length, id, experiment_name):
    base_folder = f"autopipeline-benchmarks/github-pipelines/length{length}_{id}"
    result_folder = os.path.join(base_folder, "result_archive")

    try:
        all_files = os.listdir(result_folder)
    except FileNotFoundError:
        print(f"Folder not found: {result_folder}")
        return

    pattern = re.compile(rf"{re.escape(experiment_name)}_(\d+)_target_multisource\.csv")
    tables = []

    for filename in all_files:
        match = pattern.match(filename)
        if match:
            i = int(match.group(1))
            file_path = os.path.join(result_folder, filename)
            try:
                df = pd.read_csv(file_path, low_memory=False)
                if df.columns[0].startswith("Unnamed"):
                    df = df.iloc[:, 1:]
                tables.append((i, df))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # Step 1: Schema-based bucketing (ignoring target table)
    schema_buckets = []

    for i, df in tables:
        matched = False
        for bucket in schema_buckets:
            _, rep_df = bucket[0]
            if are_schemas_similar(df.columns.tolist(), rep_df.columns.tolist()):
                bucket.append((i, df))
                matched = True
                break
        if not matched:
            schema_buckets.append([(i, df)])

    print(f" Found {len(schema_buckets)} schema-based buckets")

    # Step 2: Refine each schema bucket based on value similarity
    final_majority_group = None
    max_group_size = 0

    for bucket in schema_buckets:
        value_groups = refine_by_value_similarity(bucket, threshold=0.9)
        largest_value_group = max(value_groups, key=lambda g: len(g))

        if len(largest_value_group) > max_group_size:
            max_group_size = len(largest_value_group)
            final_majority_group = largest_value_group

    if final_majority_group:
        print(f"\n Final majority group has {len(final_majority_group)} tables.")
        print("Indices:", [i for i, _ in final_majority_group])
    else:
        print(" No valid majority group found.")
    majority_result = avg_tup_([results[i] for i, _ in final_majority_group])
    majority_index = final_majority_group[0][0]

    # score analysis calculation module
    best_score = float("-inf")
    score_index = None
    score_result = None

    for idx, result in enumerate(results):
        score = result[5]  # 6th element in the tuple
        if score >= best_score:
            best_score = score
            score_index = tables[idx][0]
            score_result = result

    # clear results directory
    for filename in all_files:
        file_path = os.path.join(result_folder, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing {file_path}: {e}")

    print(majority_index, majority_result, score_index, score_result)

    return majority_index, majority_result, score_index, score_result


def main():
    args = None  # No args needed for now

    # Sample results list (already provided by you)
    results = [
        (
            True,
            True,
            1.0,
            0.00642,
            31.59062671661377,
            3.0,
            "[\"JOIN : [['Source3_6_1', 'Source3_6_2'], ['Source3_6_1.movie id', 'Source3_6_2.movie id']]\", '\"group_by\" = [Source3_6_1.movie title], \"aggregations\" = [AVG(Source3_6_2.rating)]']",
        ),
        (
            True,
            True,
            1.0,
            0.0063896000000000005,
            19.603930234909058,
            3.0,
            '[\'JOIN : [["Source3_6_1","Source3_6_2"],["movie id","movie id"]]\', \'"group_by" = [Source3_6_1.movie_title], "aggregations" = [AVG(Source3_6_2.rating)]\']',
        ),
        (
            True,
            True,
            1.0,
            0.006166,
            13.26430058479309,
            3.0,
            '[\'JOIN : [["Source3_6_1","Source3_6_2"],["Source3_6_1.movie id","Source3_6_2.movie id"]]\', \'"group_by" = [Source3_6_1.movie title], "aggregations" = [AVG(Source3_6_2.rating)]\']',
        ),
    ]

    length = 3
    id = 6
    experiment_name = "feature_v3_4_bad_20250615_211617"

    majority_index, majority_results, score_index, score_result = analyze_results(
        args, results, length, id, experiment_name
    )

    print(f"Majority index: {majority_index}")
    print(f"Majority results: {majority_results}")
    print(f"Score index: {score_index}")
    print(f"Score results: {score_result}")


if __name__ == "__main__":
    main()
