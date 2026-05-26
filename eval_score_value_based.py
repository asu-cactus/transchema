"""
Value-based column matching with type-aware similarity.

Algorithm:
  1. For each GT column, find the best-matching generated column:
       - Categorical GT column → MinHash-estimated Jaccard on unique string values
       - Numeric GT column     → 0.5 * (JS similarity + range overlap)
  2. Build aligned dataframe D: copy matched gen column into D under GT name.
  3. Run relative_csv_score(D, df_gt) for FD and column-ratio scores.
  4. Compute per-column scores using the same metric as matching:
       - Numeric GT column    → column_score = 0.5 * (js_similarity + range_overlap)
       - Categorical GT column → column_score = MinHash Jaccard (from alignment step)
  5. true_combined_score = (fd_f1 + avg(column_score)) / 2
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

from datasketch import MinHash
from eval_score.score import relative_csv_score

SCORE_TIMEOUT = 60  # seconds
MINHASH_NUM_PERM = 128  # permutations per sketch; higher = more accurate, slower


# ---------------------------------------------------------------------------
# Type-aware column matching helpers
# ---------------------------------------------------------------------------

def _col_minhash(series: pd.Series, num_perm: int = MINHASH_NUM_PERM) -> MinHash:
    """Build a MinHash sketch from the unique string-normalised values of a column."""
    m = MinHash(num_perm=num_perm)
    for v in series.dropna():
        m.update(str(v).encode("utf-8"))
    return m


def _numeric_match_score(s_gen: pd.Series, s_gt: pd.Series) -> float:
    """
    Matching score for two numeric columns: 0.5 * (js_similarity + range_overlap).
    Returns 0.0 if either series cannot be cast to float or is empty.
    """
    try:
        v_gen = s_gen.dropna().astype(float).values
        v_gt  = s_gt.dropna().astype(float).values
    except (ValueError, TypeError):
        return 0.0

    if len(v_gen) == 0 or len(v_gt) == 0:
        return 0.0

    # Jensen-Shannon similarity
    n_bins = max(2, int(np.ceil(np.log2(min(len(v_gen), len(v_gt))) + 1)))
    lo = min(v_gen.min(), v_gt.min())
    hi = max(v_gen.max(), v_gt.max())
    if lo == hi:
        js_sim = 1.0
    else:
        pa, _ = np.histogram(v_gen, bins=n_bins, range=(lo, hi))
        pb, _ = np.histogram(v_gt,  bins=n_bins, range=(lo, hi))
        pa = pa.astype(float) + 1e-10
        pb = pb.astype(float) + 1e-10
        js_dist = float(jensenshannon(pa / pa.sum(), pb / pb.sum(), base=2))
        js_sim = round(1.0 - js_dist, 4)

    # Range overlap
    overlap = max(0.0, min(v_gen.max(), v_gt.max()) - max(v_gen.min(), v_gt.min()))
    union   = max(v_gen.max(), v_gt.max()) - min(v_gen.min(), v_gt.min())
    range_overlap = round(overlap / union, 4) if union > 0 else 1.0

    return round(0.5 * (js_sim + range_overlap), 4)


def build_jaccard_column_map(df_gen: pd.DataFrame, df_gt: pd.DataFrame,
                              num_perm: int = MINHASH_NUM_PERM) -> list:
    """
    For each GT column, find the best-matching generated column using a
    type-aware similarity metric:
      - Categorical GT column → MinHash-estimated Jaccard on unique string values
      - Numeric GT column     → 0.5 * (JS similarity + range overlap)

    A numeric gen column matched to a categorical GT column (or vice-versa)
    scores 0.0, so the matcher naturally avoids cross-type pairings.

    Returns:
        list of dicts: [{"gt_col": str, "gen_col": str, "jaccard": float}, ...]
        ordered by df_gt.columns  ("jaccard" holds the match score regardless of type)
    """
    # Pre-build MinHash only for categorical columns (numeric matching is on-the-fly)
    gt_numeric  = {col: np.issubdtype(df_gt[col].dtype,  np.number) for col in df_gt.columns}
    gen_numeric = {col: np.issubdtype(df_gen[col].dtype, np.number) for col in df_gen.columns}

    gt_minhashes  = {col: _col_minhash(df_gt[col],  num_perm)
                     for col in df_gt.columns  if not gt_numeric[col]}
    gen_minhashes = {col: _col_minhash(df_gen[col], num_perm)
                     for col in df_gen.columns if not gen_numeric[col]}

    mapping = []
    for gt_col in df_gt.columns:
        best_gen_col = None
        best_score   = -1.0

        for gen_col in df_gen.columns:
            if gt_numeric[gt_col]:
                # Numeric GT: only consider numeric gen columns
                if not gen_numeric[gen_col]:
                    score = 0.0
                else:
                    score = _numeric_match_score(df_gen[gen_col], df_gt[gt_col])
            else:
                # Categorical GT: only consider categorical gen columns via MinHash
                if gen_numeric[gen_col]:
                    score = 0.0
                else:
                    score = gt_minhashes[gt_col].jaccard(gen_minhashes[gen_col])

            if score > best_score:
                best_score   = score
                best_gen_col = gen_col

        mapping.append({
            "gt_col":  gt_col,
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
# Per-column scoring
# ---------------------------------------------------------------------------

def _compute_column_scores(df_aligned: pd.DataFrame, df_gt: pd.DataFrame,
                            pairs: list, column_map: list) -> dict:
    """
    Compute a score for every GT column:
      - Numeric GT column   → column_score = 0.5 * (js_similarity + range_overlap)
      - Categorical GT column → column_score = Jaccard similarity (from column_map)

    pairs: list of (gen_col, gt_col) name tuples (aligned names — gen_col == gt_col)
    column_map: output of build_jaccard_column_map (for categorical Jaccard lookup)

    Returns:
        dict with keys:
          "per_column"      → {gt_col: {...details...}}
          "avg_column_score"→ float | None
          "avg_js_similarity"    → float | None  (numeric cols only, for debug)
          "avg_range_overlap"    → float | None  (numeric cols only, for debug)
    """
    jaccard_lookup = {entry["gt_col"]: entry["jaccard"] for entry in column_map}

    per_column = {}

    for gen_col, gt_col in pairs:
        if gen_col not in df_aligned.columns or gt_col not in df_gt.columns:
            continue

        gen_series = df_aligned[gen_col]
        gt_series  = df_gt[gt_col]
        gt_numeric = np.issubdtype(gt_series.dtype, np.number)

        # ── Categorical ───────────────────────────────────────────────────────
        if not gt_numeric:
            jaccard = jaccard_lookup.get(gt_col, 0.0)
            per_column[gt_col] = {
                "type":         "categorical",
                "gen_col":      gen_col,
                "column_score": round(float(jaccard), 4),
                "jaccard":      round(float(jaccard), 4),
            }
            continue

        # ── Numeric ───────────────────────────────────────────────────────────
        _zero = {
            "type":                    "numeric",
            "gen_col":                 gen_col,
            "column_score":            0.0,
            "js_similarity":           0.0,
            "range_overlap":           0.0,
            "wasserstein_normalized":  None,
            "gen_stats":               None,
            "gt_stats":                None,
        }

        if not np.issubdtype(gen_series.dtype, np.number):
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

        # Jensen-Shannon similarity
        n_bins = max(2, int(np.ceil(np.log2(min(len(gen_vals), len(gt_vals))) + 1)))
        lo = min(gen_vals.min(), gt_vals.min())
        hi = max(gen_vals.max(), gt_vals.max())
        if lo == hi:
            js_similarity = 1.0
        else:
            pa, _ = np.histogram(gen_vals, bins=n_bins, range=(lo, hi))
            pb, _ = np.histogram(gt_vals,  bins=n_bins, range=(lo, hi))
            pa = pa.astype(float) + 1e-10
            pb = pb.astype(float) + 1e-10
            js_dist = float(jensenshannon(pa / pa.sum(), pb / pb.sum(), base=2))
            js_similarity = round(1.0 - js_dist, 4)

        # Range overlap
        gen_min, gen_max = float(gen_vals.min()), float(gen_vals.max())
        gt_min,  gt_max  = float(gt_vals.min()),  float(gt_vals.max())
        overlap = max(0.0, min(gen_max, gt_max) - max(gen_min, gt_min))
        union   = max(gen_max, gt_max) - min(gen_min, gt_min)
        range_overlap = round(overlap / union, 4) if union > 0 else 1.0

        # Wasserstein (debug only)
        w = wasserstein_distance(gen_vals, gt_vals)
        r = max(float(gen_vals.max() - gen_vals.min()),
                float(gt_vals.max()  - gt_vals.min()), 1e-10)
        w_norm = w / r

        column_score = round(0.5 * (js_similarity + range_overlap), 4)

        per_column[gt_col] = {
            "type":                   "numeric",
            "gen_col":                gen_col,
            "column_score":           column_score,
            "js_similarity":          js_similarity,
            "range_overlap":          range_overlap,
            "wasserstein_normalized": round(w_norm, 4),
            "gen_stats": {
                "min":  round(gen_min, 4),
                "max":  round(gen_max, 4),
                "mean": round(float(gen_vals.mean()), 4),
            },
            "gt_stats": {
                "min":  round(gt_min, 4),
                "max":  round(gt_max, 4),
                "mean": round(float(gt_vals.mean()), 4),
            },
        }

    if per_column:
        avg_column_score = round(
            sum(v["column_score"] for v in per_column.values()) / len(per_column), 4
        )
        numeric_cols = [v for v in per_column.values() if v["type"] == "numeric"]
        if numeric_cols:
            avg_js_sim       = round(sum(v["js_similarity"]  for v in numeric_cols) / len(numeric_cols), 4)
            avg_range_overlap = round(sum(v["range_overlap"] for v in numeric_cols) / len(numeric_cols), 4)
        else:
            avg_js_sim = avg_range_overlap = None
    else:
        avg_column_score = avg_js_sim = avg_range_overlap = None

    return {
        "per_column":          per_column,
        "avg_column_score":    avg_column_score,
        "avg_js_similarity":   avg_js_sim,
        "avg_range_overlap":   avg_range_overlap,
    }


# ---------------------------------------------------------------------------
# Main scoring entry point
# ---------------------------------------------------------------------------

def value_based_relative_csv_score(df_gen: pd.DataFrame, df_gt: pd.DataFrame):
    """
    Drop-in replacement for relative_csv_score.

    1. Align df_gen columns to df_gt via Jaccard similarity on unique values.
    2. Call relative_csv_score(D, df_gt) for FD and column-ratio scores.
    3. Compute per-column scores:
         numeric   → 0.5 * (js_similarity + range_overlap)
         categorical → Jaccard similarity (from alignment step)
    4. true_combined_score = (fd_f1 + avg(column_score)) / 2

    Returns the same 6-tuple as relative_csv_score:
        (fd_ratio, col_ratio, combined_score, fd_f1, true_combined_score, debug_dict)
    """
    if df_gen is None or df_gt is None or len(df_gen) == 0 or len(df_gt) == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0, {"error": "empty or None dataframe", "jaccard_column_map": []}

    column_map = build_jaccard_column_map(df_gen, df_gt)
    df_aligned = build_aligned_dataframe(df_gen, column_map)

    fd_ratio, col_ratio, combined_score, fd_f1, _, debug_dict = \
        relative_csv_score(df_aligned, df_gt)

    pairs = [(col, col) for col in df_gt.columns if col in df_aligned.columns]
    col_scores = _compute_column_scores(df_aligned, df_gt, pairs, column_map)

    avg_column_score = col_scores.get("avg_column_score")

    if avg_column_score is not None:
        true_combined_score = round((fd_f1 + avg_column_score) / 2, 4)
    else:
        true_combined_score = round(fd_f1, 4)

    debug_dict["column_scores"]       = col_scores
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
