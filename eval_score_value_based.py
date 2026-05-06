"""
Value-based column matching via Jaccard similarity.

Algorithm:
  1. For each column c in the target (GT) dataframe, find the column in the
     generated dataframe with the highest Jaccard similarity on unique values.
  2. Build aligned dataframe D: copy that gen column's data into D under the name c.
  3. Run relative_csv_score(D, df_gt) for FD and column-ratio scores.
  4. Override the distribution score using a value_based variant:
       - GT column NOT numeric  → skip (no distribution signal)
       - GT column numeric, gen column NOT numeric or conversion fails → score 0.0
       - Both numeric → full JS / range-overlap / Wasserstein calculation
"""

import sys
import os

import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from scipy.stats import wasserstein_distance
from scipy.spatial.distance import jensenshannon

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from eval_score.score import relative_csv_score

SCORE_TIMEOUT = 60  # seconds


# ---------------------------------------------------------------------------
# Jaccard column matching
# ---------------------------------------------------------------------------

def _col_value_set(series: pd.Series) -> set:
    return set(str(v) for v in series.dropna())


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def build_jaccard_column_map(df_gen: pd.DataFrame, df_gt: pd.DataFrame) -> list:
    """
    For each GT column, find the generated column with the highest Jaccard
    similarity on unique string-normalized values.

    Returns:
        list of dicts: [{"gt_col": str, "gen_col": str, "jaccard": float}, ...]
        ordered by df_gt.columns
    """
    gt_sets = {col: _col_value_set(df_gt[col]) for col in df_gt.columns}
    gen_sets = {col: _col_value_set(df_gen[col]) for col in df_gen.columns}

    mapping = []
    for gt_col in df_gt.columns:
        best_gen_col = None
        best_score = -1.0
        for gen_col in df_gen.columns:
            j = _jaccard(gt_sets[gt_col], gen_sets[gen_col])
            if j > best_score:
                best_score = j
                best_gen_col = gen_col
        mapping.append({
            "gt_col": gt_col,
            "gen_col": best_gen_col,
            "jaccard": round(best_score, 4),
        })
    return mapping


def build_aligned_dataframe(df_gen: pd.DataFrame, column_map: list) -> pd.DataFrame:
    """
    Build aligned dataframe D:
      for each GT column c → copy the matched gen column's data into D under name c.
    GT columns with no match receive an all-NaN column.
    """
    aligned = {}
    for entry in column_map:
        gt_col = entry["gt_col"]
        gen_col = entry["gen_col"]
        if gen_col is not None and gen_col in df_gen.columns:
            aligned[gt_col] = df_gen[gen_col].values
        else:
            aligned[gt_col] = [None] * len(df_gen)
    return pd.DataFrame(aligned)


# ---------------------------------------------------------------------------
# Value-based distribution scoring
# ---------------------------------------------------------------------------

def _compute_distribution_scores_value_based(df_a: pd.DataFrame, df_b: pd.DataFrame,
                                              pairs: list) -> dict:
    """
    Distribution scoring with GT-dtype-driven rules:
      - GT column NOT numeric  → skip column (no distribution signal)
      - GT column numeric, gen NOT numeric or conversion fails → record 0.0
      - Both numeric → full JS divergence / range-overlap / Wasserstein calculation

    pairs: list of (gen_col, gt_col) name tuples
    """
    per_column = {}

    for gen_col, gt_col in pairs:
        if gen_col not in df_a.columns or gt_col not in df_b.columns:
            continue

        gen_series = df_a[gen_col]
        gt_series  = df_b[gt_col]

        gt_numeric  = np.issubdtype(gt_series.dtype, np.number)
        gen_numeric = np.issubdtype(gen_series.dtype, np.number)

        if not gt_numeric:
            continue  # non-numeric GT columns carry no distribution signal

        _zero = {
            "gen_col": gen_col,
            "distribution_similarity": 0.0,
            "js_similarity":           0.0,
            "range_overlap":           0.0,
            "wasserstein_normalized":  None,
            "gen_stats": None,
            "gt_stats":  None,
        }

        if not gen_numeric:
            per_column[gt_col] = _zero
            continue

        try:
            gen_vals = gen_series.dropna().astype(float).values
            gt_vals  = gt_series.dropna().astype(float).values
        except (ValueError, TypeError):
            per_column[gt_col] = _zero
            continue

        if len(gen_vals) == 0 or len(gt_vals) == 0:
            per_column[gt_col] = _zero
            continue

        w = wasserstein_distance(gen_vals, gt_vals)
        gen_range = float(gen_vals.max() - gen_vals.min())
        gt_range  = float(gt_vals.max()  - gt_vals.min())
        r = max(gen_range, gt_range, 1e-10)
        w_norm = w / r
        similarity = max(0.0, 1.0 - min(w_norm, 1.0))

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
        avg_sim          = round(sum(v["distribution_similarity"] for v in per_column.values()) / len(per_column), 4)
        avg_js_sim       = round(sum(v["js_similarity"]           for v in per_column.values()) / len(per_column), 4)
        avg_range_overlap = round(sum(v["range_overlap"]          for v in per_column.values()) / len(per_column), 4)
    else:
        avg_sim = avg_js_sim = avg_range_overlap = None

    return {
        "per_column":               per_column,
        "avg_distribution_similarity": avg_sim,
        "avg_js_similarity":           avg_js_sim,
        "avg_range_overlap":           avg_range_overlap,
    }


# ---------------------------------------------------------------------------
# Main scoring entry point
# ---------------------------------------------------------------------------

def value_based_relative_csv_score(df_gen: pd.DataFrame, df_gt: pd.DataFrame):
    """
    Drop-in replacement for relative_csv_score.

    1. Align df_gen columns to df_gt via Jaccard similarity.
    2. Call relative_csv_score(D, df_gt) for FD and column-ratio scores.
    3. Override distribution with _compute_distribution_scores_value_based,
       which assigns 0.0 when the gen column dtype doesn't match the GT's
       numeric expectation instead of silently skipping.
    4. Recompute true_combined_score = (fd_f1 + range_overlap + js_sim) / 3.

    Returns the same 6-tuple as relative_csv_score:
        (fd_ratio, col_ratio, combined_score, fd_f1, true_combined_score, debug_dict)
    """
    if df_gen is None or df_gt is None or len(df_gen) == 0 or len(df_gt) == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0, {"error": "empty or None dataframe", "jaccard_column_map": []}

    column_map = build_jaccard_column_map(df_gen, df_gt)
    df_aligned = build_aligned_dataframe(df_gen, column_map)

    # FD mining and column ratio from existing scorer (unchanged)
    fd_ratio, col_ratio, combined_score, fd_f1, _, debug_dict = \
        relative_csv_score(df_aligned, df_gt)

    # Override distribution using value_based rules.
    # df_aligned has the same column names as df_gt by construction.
    pairs = [(col, col) for col in df_gt.columns if col in df_aligned.columns]
    dist_info = _compute_distribution_scores_value_based(df_aligned, df_gt, pairs)

    js_sim        = dist_info.get("avg_js_similarity")
    range_overlap = dist_info.get("avg_range_overlap")

    if range_overlap is not None and js_sim is not None:
        true_combined_score = round((fd_f1 + range_overlap + js_sim) / 3, 4)
    elif range_overlap is not None:
        true_combined_score = round((fd_f1 + range_overlap) / 2, 4)
    elif js_sim is not None:
        true_combined_score = round((fd_f1 + js_sim) / 2, 4)
    else:
        true_combined_score = round(fd_f1, 4)

    debug_dict["distribution"]        = dist_info
    debug_dict["true_combined_score"] = true_combined_score
    debug_dict["jaccard_column_map"]  = column_map

    return fd_ratio, col_ratio, combined_score, fd_f1, true_combined_score, debug_dict


def value_based_relative_csv_score_timed(df_gen: pd.DataFrame, df_gt: pd.DataFrame,
                                          timeout: int = SCORE_TIMEOUT):
    """
    Calls value_based_relative_csv_score with a hard timeout.
    Raises TimeoutError if scoring exceeds `timeout` seconds (default 60 s).
    """
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(value_based_relative_csv_score, df_gen, df_gt)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            raise TimeoutError(f"value_based_relative_csv_score timed out after {timeout}s")
