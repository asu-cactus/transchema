import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

import numpy as np
from scipy.stats import wasserstein_distance
from scipy.spatial.distance import jensenshannon

# Ensure this directory is on sys.path so fdtool and column_map_utils are importable
_SCORE_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCORE_DIR not in sys.path:
    sys.path.insert(0, _SCORE_DIR)

import fdtool.fdtool as fdtool
import column_map_utils
from column_map_utils import get_column_map

FD_TIMEOUT = 60

def _run_fdtool(df):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fdtool.main, df)
        try:
            return future.result(timeout=FD_TIMEOUT)
        except FuturesTimeoutError:
            return [], [], []

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
            candidates.append({
                "left_column": pair.col_l.col_name,
                "right_column": pair.col_r.col_name,
                "jaccard": pair.jaccard_value,
                "range_overlap": pair.range_overlap,
                "pattern_value": pair.pattern_value,
            })
        serialized.append({
            "right_column": right_col,
            "candidates": candidates
        })
    return serialized
MAX_FD_COLS = 52


def compute_distribution_scores(df_a, df_b, col_map=None):
    """
    Compute per-column normalized Wasserstein distance for numerical columns
    that appear in both the generated (df_a) and ground-truth (df_b) tables.

    Matching uses the column map when available, otherwise falls back to
    shared column names.

    Returns a dict:
      {
        "per_column": {
          "<gt_col>": {
            "gen_col": str,
            "distribution_similarity": float,   # 1.0 = identical, 0.0 = maximally different
            "gen_stats":  {"min": float, "max": float, "mean": float},
            "gt_stats":   {"min": float, "max": float, "mean": float},
            "wasserstein_normalized": float,
          }, ...
        },
        "avg_distribution_similarity": float,   # mean over matched numerical columns
      }
    """
    per_column = {}

    # Build (gen_col, gt_col) pairs to compare
    pairs = []
    if col_map:
        for candidate_group in col_map:
            if not candidate_group:
                continue
            gt_col = candidate_group[0].col_r.col_name
            gen_col = candidate_group[0].col_l.col_name
            pairs.append((gen_col, gt_col))
    else:
        shared = set(df_a.columns) & set(df_b.columns)
        pairs = [(c, c) for c in shared]

    for gen_col, gt_col in pairs:
        if gen_col not in df_a.columns or gt_col not in df_b.columns:
            continue

        gen_series = df_a[gen_col]
        gt_series  = df_b[gt_col]

        # Only process numerical columns
        if not (np.issubdtype(gen_series.dtype, np.number) or
                np.issubdtype(gt_series.dtype, np.number)):
            continue

        try:
            gen_vals = gen_series.dropna().astype(float).values
            gt_vals  = gt_series.dropna().astype(float).values
        except (ValueError, TypeError):
            continue

        if len(gen_vals) == 0 or len(gt_vals) == 0:
            continue

        w = wasserstein_distance(gen_vals, gt_vals)

        # Normalize by the larger range of either distribution
        gen_range = float(gen_vals.max() - gen_vals.min())
        gt_range  = float(gt_vals.max()  - gt_vals.min())
        r = max(gen_range, gt_range, 1e-10)
        w_norm = w / r
        similarity = max(0.0, 1.0 - min(w_norm, 1.0))

        # JS distance (log base 2) → similarity = 1 - js_distance, naturally in [0, 1]
        n_bins = max(2, int(np.ceil(np.log2(min(len(gen_vals), len(gt_vals))) + 1)))
        lo = min(gen_vals.min(), gt_vals.min())
        hi = max(gen_vals.max(), gt_vals.max())
        if lo == hi:
            js_similarity = 1.0
        else:
            pa, _ = np.histogram(gen_vals.astype(float), bins=n_bins, range=(lo, hi))
            pb, _ = np.histogram(gt_vals.astype(float),  bins=n_bins, range=(lo, hi))
            pa = pa.astype(float) + 1e-10
            pb = pb.astype(float) + 1e-10
            js_dist = float(jensenshannon(pa / pa.sum(), pb / pb.sum(), base=2))
            js_similarity = round(1.0 - js_dist, 4)

        # Value range overlap (Jaccard of [min, max] intervals) — numerical only
        gen_min, gen_max = float(gen_vals.min()), float(gen_vals.max())
        gt_min,  gt_max  = float(gt_vals.min()),  float(gt_vals.max())
        overlap = max(0.0, min(gen_max, gt_max) - max(gen_min, gt_min))
        union   = max(gen_max, gt_max) - min(gen_min, gt_min)
        range_overlap = round(overlap / union, 4) if union > 0 else 1.0

        per_column[gt_col] = {
            "gen_col":  gen_col,
            "distribution_similarity": round(similarity, 4),
            "js_similarity":           js_similarity,
            "range_overlap":           range_overlap,
            "wasserstein_normalized":  round(w_norm, 4),
            "gen_stats": {
                "min":  round(gen_min,  4),
                "max":  round(gen_max,  4),
                "mean": round(float(gen_vals.mean()), 4),
            },
            "gt_stats": {
                "min":  round(gt_min,  4),
                "max":  round(gt_max,  4),
                "mean": round(float(gt_vals.mean()), 4),
            },
        }

    if per_column:
        avg_sim = round(
            sum(v["distribution_similarity"] for v in per_column.values()) / len(per_column), 4
        )
        avg_js_sim = round(
            sum(v["js_similarity"] for v in per_column.values()) / len(per_column), 4
        )
        avg_range_overlap = round(
            sum(v["range_overlap"] for v in per_column.values()) / len(per_column), 4
        )
    else:
        avg_sim           = None
        avg_js_sim        = None
        avg_range_overlap = None

    return {
        "per_column": per_column,
        "avg_distribution_similarity": avg_sim,
        "avg_js_similarity":           avg_js_sim,
        "avg_range_overlap":           avg_range_overlap,
    }


def relative_csv_score(df_a, df_b):
    column_map_utils.GLOBAL_SUMMARY = None  # Reset the actual module-level cache

    # Truncate columns to fdtool's supported limit (no row truncation)
    df_a_fd = df_a.iloc[:, :MAX_FD_COLS]
    df_b_fd = df_b.iloc[:, :MAX_FD_COLS]

    # Run FD mining with hard 60s timeout
    FDs_a, E_a, keys_a = _run_fdtool(df_a_fd)
    FDs_b, E_b, keys_b = _run_fdtool(df_b_fd)

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

    if len(truth_fds) == 0:
        fd_f1 = 1.0
        precision = 1.0
        recall = 1.0
    else:
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

    distribution_info = compute_distribution_scores(df_a, df_b, col_map)
    js_sim        = distribution_info.get("avg_js_similarity")
    range_overlap = distribution_info.get("avg_range_overlap")
    if js_sim is not None and range_overlap is not None:
        true_combined_score = round((fd_f1 + col_ratio + js_sim + range_overlap) / 4, 4)
    elif js_sim is not None:
        true_combined_score = round((fd_f1 + col_ratio + js_sim) / 3, 4)
    else:
        true_combined_score = round((fd_f1 + col_ratio) / 2, 4)

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
        "distribution": distribution_info,
    }

    return fd_ratio, col_ratio, combined_score, fd_f1, true_combined_score, debug_dict


def summarize_score(debug_dict: dict, score: float, fd_f1: float, col_ratio: float) -> dict:
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
    missed_fds = fd_section.get("false_negatives", [])   # in ground truth but not in output
    unexpected_fds = fd_section.get("false_positives", [])  # in output but not in ground truth

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

