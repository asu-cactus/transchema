from quality.quality import analyze_functional_dependencies
from valentine import valentine_match, algorithms
import sys


def normalize_fd_list(fd_list):
    """
    Convert [(key_tuple, rhs), ...] into a set of
    ((sorted_key_tuple), rhs), so key‐order is ignored.
    """
    return {(tuple(sorted(key)), rhs) for key, rhs in fd_list}


def normalize_keys(fd_set):
    """
    Extract just the sorted key tuples from your FD‐set.
    """
    return {key for key, _ in fd_set}


def extract_dependencies(fd_dict):
    dependencies = set()  # Use a set to avoid duplicates
    for determinant, dependents in fd_dict.items():
        for dependent in dependents:
            dependencies.add((determinant, dependent))
    return dependencies


def calculate_score(gt_df, tgt_df):

    max_rows = min(100, gt_df.shape[0])
    gt_df = gt_df.iloc[:max_rows, :15]

    max_rows = min(100, tgt_df.shape[0])
    tgt_df = tgt_df.iloc[:max_rows, :15]

    # parameters
    w1 = 1
    w2 = 1
    w3 = 1
    p = 1

    # Match Functional Dependencies
    fd_gt, key_gt = analyze_functional_dependencies(gt_df)
    fd_tgt, key_tgt = analyze_functional_dependencies(tgt_df)

    print("\n\n\nScore Calculation\n\n\n")

    print(fd_gt)
    print(key_gt)
    print("\n\nTransformed : ")
    print(fd_tgt)
    print(key_tgt)

    # sys.exit()

    # dependencies_gt = {(tuple(key), tuple(value)) for key, value in fd_gt}
    # dependencies_tgt = {(tuple(key), tuple(value)) for key, value in fd_tgt}

    # print("\n\nDependencies GT : ", dependencies_gt)
    # print("Dependencies TGT : ", dependencies_tgt)

    set_gt = normalize_fd_list(fd_gt)
    set_tgt = normalize_fd_list(fd_tgt)

    # ── FD intersection & union ───────────────────────────────────────────────
    intersection_fds = set_gt & set_tgt
    union_fds = set_gt | set_tgt

    # ── Now extract just the keys from each normalized FD set ────────────────
    keys1 = normalize_keys(set_gt)
    keys2 = normalize_keys(set_tgt)

    # ── Key intersection & union ─────────────────────────────────────────────
    intersection_keys = keys1 & keys2
    union_keys = keys1 | keys2

    score_fd = len(intersection_fds) / len(union_fds) if (len(union_fds) > 0) else 1
    score_key = len(intersection_keys) / len(union_keys) if (len(union_keys) > 0) else 1

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
    import pandas as pd

    gt_df = pd.read_csv(
        "/home/local/ASUAD/jrtandel/transchema/autopipeline-benchmarks/github-pipelines/length1_23/target.csv",
    )
    gt_df = gt_df.drop(columns=["Unnamed: 0"], errors="ignore")
    tgt_df = pd.read_csv(
        "/home/local/ASUAD/jrtandel/transchema/autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_critique_soft.csv",
    )

    print(gt_df, tgt_df)

    score = calculate_score(gt_df, tgt_df)
    print(f"Score: {score}")
