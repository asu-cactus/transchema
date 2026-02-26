import json
import fdtool.fdtool as fdtool
import column_map_utils
from column_map_utils import get_column_map


def serialize_fd_list(fd_list):
    return [{"lhs": list(lhs), "rhs": rhs} for lhs, rhs in fd_list]


def serialize_equivalences(e_list):
    safe = []
    for item in e_list:
        try:
            left, right = item
            safe.append({"left": list(left), "right": list(right)})
        except Exception:
            safe.append(str(item))
    return safe


def serialize_column_map(col_map):
    serialized = []
    for candidate_group in col_map:
        if not candidate_group:
            continue
        right_col = candidate_group[0].col_r.col_name
        candidates = []
        for pair in candidate_group:
            candidates.append(
                {
                    "left_column": pair.col_l.col_name,
                    "right_column": pair.col_r.col_name,
                    "jaccard": pair.jaccard_value,
                    "range_overlap": pair.range_overlap,
                    "pattern_value": pair.pattern_value,
                }
            )
        serialized.append({"right_column": right_col, "candidates": candidates})
    return serialized


def relative_csv_score(df_a, df_b):
    # Truncate to cap scoring time
    df_a = df_a.iloc[:2000, :15]
    df_b = df_b.iloc[:2000, :15]

    column_map_utils.GLOBAL_SUMMARY = None  # Reset the actual module-level cache

    # Run FD mining
    FDs_a, E_a, keys_a = fdtool.main(df_a)
    FDs_b, E_b, keys_b = fdtool.main(df_b)

    fd_count_a = len(FDs_a)
    fd_count_b = len(FDs_b)

    fd_ratio = fd_count_a / max(fd_count_b, 1)

    # FD F1 Score
    def canonical_fd(fd_list):
        return set([tuple(sorted(lhs)) + (rhs,) for lhs, rhs in fd_list])

    gen_fds = canonical_fd(FDs_a)
    truth_fds = canonical_fd(FDs_b)

    tp = len(gen_fds & truth_fds)
    fp = len(gen_fds - truth_fds)
    fn = len(truth_fds - gen_fds)

    precision = tp / max(len(gen_fds), 1)
    recall = tp / max(len(truth_fds), 1)
    fd_f1 = 2 * precision * recall / max(precision + recall, 1e-6)

    # FD False Positives / False Negatives
    def serialize_fd_tuples(fd_tuples):
        return [{"lhs": list(lhs[:-1]), "rhs": lhs[-1]} for lhs in fd_tuples]

    fd_false_positives = serialize_fd_tuples(gen_fds - truth_fds)
    fd_false_negatives = serialize_fd_tuples(truth_fds - gen_fds)

    # Column map ratio
    col_map = get_column_map(df_a, df_b)
    column_map_utils.GLOBAL_SUMMARY = None  # Reset so self-map recomputes from df_b
    self_col_map = get_column_map(df_b, df_b)

    col_count = len(col_map)
    self_col_count = len(self_col_map)
    col_ratio = col_count / max(self_col_count, 1)

    combined_score = (fd_ratio + col_ratio) / 2
    true_combined_score = (fd_f1 + col_ratio) / 2  # new score using FD F1

    debug_dict = {
        "fd": {
            "A": {
                "count": fd_count_a,
                "fds": serialize_fd_list(FDs_a),
                "equivalences": serialize_equivalences(E_a),
                "keys": keys_a,
            },
            "B": {
                "count": fd_count_b,
                "fds": serialize_fd_list(FDs_b),
                "equivalences": serialize_equivalences(E_b),
                "keys": keys_b,
            },
            "ratio": fd_ratio,
            "precision": precision,
            "recall": recall,
            "f1": fd_f1,
            "false_positives": fd_false_positives,
            "false_negatives": fd_false_negatives,
        },
        "columns": {
            "A_to_B": {
                "count": col_count,
                "map": serialize_column_map(col_map),
            },
            "B_to_B": {
                "count": self_col_count,
                "map": serialize_column_map(self_col_map),
            },
            "ratio": col_ratio,
        },
        "combined_score": combined_score,
        "true_combined_score": true_combined_score,
    }

    return fd_ratio, col_ratio, combined_score, fd_f1, true_combined_score, debug_dict


def summarize_score(
    debug_dict: dict, score: float, fd_f1: float, col_ratio: float
) -> dict:
    """Convert raw score debug dict into a clean, LLM-readable summary.

    Returns a dict with counts and missed items for functional dependencies,
    keys, and column mappings — using full terms (no abbreviations).
    """
    fd_section = debug_dict.get("fd", {})
    columns_section = debug_dict.get("columns", {})

    # Functional dependencies
    output_fd_count = fd_section.get("A", {}).get("count", 0)
    gt_fd_count = fd_section.get("B", {}).get("count", 0)
    output_keys = fd_section.get("A", {}).get("keys", [])
    gt_keys = fd_section.get("B", {}).get("keys", [])
    missed_fds = fd_section.get(
        "false_negatives", []
    )  # in ground truth but not in output
    unexpected_fds = fd_section.get(
        "false_positives", []
    )  # in output but not in ground truth

    def format_fd(fd):
        lhs = ", ".join(fd["lhs"])
        return f"({lhs}) -> {fd['rhs']}"

    def format_key(key):
        return "[" + ", ".join(key) + "]"

    # Missed keys: keys in ground truth but not in output
    gt_keys_set = {frozenset(k) for k in gt_keys}
    output_keys_set = {frozenset(k) for k in output_keys}
    missed_key_sets = gt_keys_set - output_keys_set
    missed_keys = sorted([format_key(sorted(k)) for k in missed_key_sets])

    # Column mappings
    a_to_b_count = columns_section.get("A_to_B", {}).get("count", 0)
    b_to_b_count = columns_section.get("B_to_B", {}).get("count", 0)
    a_to_b_map = columns_section.get("A_to_B", {}).get("map", [])
    b_to_b_map = columns_section.get("B_to_B", {}).get("map", [])

    matched_gt_columns = {entry["right_column"] for entry in a_to_b_map}
    all_gt_columns = {entry["right_column"] for entry in b_to_b_map}
    missed_target_columns = sorted(all_gt_columns - matched_gt_columns)

    return {
        "overall_score": round(float(score), 4),
        "functional_dependency_f1_score": round(float(fd_f1), 4),
        "column_mapping_score": round(float(col_ratio), 4),
        "functional_dependencies": {
            "ground_truth_count": gt_fd_count,
            "output_count": output_fd_count,
            "missed": [format_fd(fd) for fd in missed_fds],
            "unexpected": [format_fd(fd) for fd in unexpected_fds],
        },
        "keys": {
            "ground_truth_keys": [format_key(k) for k in gt_keys],
            "output_keys": [format_key(k) for k in output_keys],
            "missed_ground_truth_keys": missed_keys,
        },
        "column_mappings": {
            "matched_count": a_to_b_count,
            "total_target_columns": b_to_b_count,
            "missed_target_columns": missed_target_columns,
        },
    }
