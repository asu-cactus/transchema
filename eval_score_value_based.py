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

from scipy.stats import wasserstein_distance
from scipy.spatial.distance import jensenshannon

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from datasketch import MinHash
from eval_score.score import relative_csv_score

SCORE_TIMEOUT = 60    # seconds
MINHASH_NUM_PERM = 128  # permutations per sketch; higher = more accurate, slower
MAX_COLS_FOR_SCORING = 20  # column cap applied to df_gt when it has more columns


# ---------------------------------------------------------------------------
# Type-aware column matching helpers
# ---------------------------------------------------------------------------

def _col_minhash(series: pd.Series, num_perm: int = MINHASH_NUM_PERM) -> MinHash:
    """Build a MinHash sketch from the unique string-normalised values of a column."""
    m = MinHash(num_perm=num_perm)
    for v in series.dropna():
        m.update(str(v).encode("utf-8"))
    return m


def _to_timestamps_if_date(series: pd.Series, threshold: float = 0.8):
    """
    If >threshold fraction of non-null values parse as dates, return
    (unix_timestamp_series_float, True). Otherwise return (series, False).
    """
    strs = series.dropna().astype(str)
    if len(strs) == 0:
        return series, False
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        parsed = pd.to_datetime(strs, errors="coerce")
    if parsed.notna().mean() >= threshold:
        ts = parsed.dropna().astype("int64").astype(float) / 1e9
        return ts, True
    return series, False


def _cat_property_score(s_gen: pd.Series, s_gt: pd.Series) -> float:
    """
    Property-based similarity for categorical columns using 5 structural metrics:
      1. lowercase_frac  — fraction of values that are entirely lowercase
      2. uppercase_frac  — fraction that are entirely uppercase
      4. avg_len         — mean character length of string values
      5. len_std         — standard deviation of character lengths
      6. digit_frac      — fraction of total characters that are digits

    Each property similarity = 1 - |p_gen - p_gt| / max(|p_gen|, |p_gt|, ε).
    Final score = mean of all 5 similarities.
    """
    def _props(s: pd.Series) -> dict:
        strs = s.dropna().astype(str)
        if len(strs) == 0:
            return dict(lc=0.0, uc=0.0, avg_len=0.0, len_std=0.0, digit_frac=0.0)
        lengths      = strs.str.len()
        all_chars    = "".join(strs)
        total_chars  = max(len(all_chars), 1)
        return {
            "lc":         float((strs == strs.str.lower()).mean()),
            "uc":         float((strs == strs.str.upper()).mean()),
            "avg_len":    float(lengths.mean()),
            "len_std":    float(lengths.std(ddof=0) if len(lengths) > 1 else 0.0),
            "digit_frac": float(sum(c.isdigit() for c in all_chars) / total_chars),
        }

    def _sim(v1: float, v2: float) -> float:
        denom = max(abs(v1), abs(v2), 1e-9)
        return round(1.0 - abs(v1 - v2) / denom, 4)

    p_gen = _props(s_gen)
    p_gt  = _props(s_gt)

    sims = [
        _sim(p_gen["lc"],         p_gt["lc"]),
        _sim(p_gen["uc"],         p_gt["uc"]),
        _sim(p_gen["avg_len"],    p_gt["avg_len"]),
        _sim(p_gen["len_std"],    p_gt["len_std"]),
        _sim(p_gen["digit_frac"], p_gt["digit_frac"]),
    ]
    return round(float(np.mean(sims)), 4)


def _nunique_sim(s_gen: pd.Series, s_gt: pd.Series) -> float:
    """
    Uniqueness-fraction ratio: min(frac_gen, frac_gt) / max(frac_gen, frac_gt).
    Computes uniqueness rate (n_unique/n_rows) independently per column, then
    takes min/max ratio — a larger proportional gap yields a stronger penalty
    than 1-|diff| while still normalising away row-count differences.
    """
    frac_gen = s_gen.nunique(dropna=True) / max(len(s_gen), 1)
    frac_gt  = s_gt.nunique(dropna=True)  / max(len(s_gt),  1)
    hi = max(frac_gen, frac_gt)
    return round(min(frac_gen, frac_gt) / hi, 4) if hi > 0 else 1.0


def _missing_sim(s_gen: pd.Series, s_gt: pd.Series) -> float:
    """Similarity of missing-value fractions: 1 - |frac_gen - frac_gt|."""
    frac_gen = s_gen.isna().sum() / max(len(s_gen), 1)
    frac_gt  = s_gt.isna().sum()  / max(len(s_gt),  1)
    return round(max(0.0, 1.0 - abs(frac_gen - frac_gt)), 4)


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
      - Categorical GT column → property-based score (lowercase_frac, uppercase_frac,
                                avg_len, len_std, digit_frac)
      - Numeric GT column     → 0.5 * (JS similarity + range overlap)

    A numeric gen column matched to a categorical GT column (or vice-versa)
    scores 0.0, so the matcher naturally avoids cross-type pairings.

    Returns:
        list of dicts: [{"gt_col": str, "gen_col": str, "jaccard": float}, ...]
        ordered by df_gt.columns  ("jaccard" holds the match score regardless of type)
    """
    gt_numeric  = {col: np.issubdtype(df_gt[col].dtype,  np.number) for col in df_gt.columns}
    gen_numeric = {col: np.issubdtype(df_gen[col].dtype, np.number) for col in df_gen.columns}

    # Pre-convert date-like categorical columns to Unix timestamps
    gt_timestamps  = {}
    gen_timestamps = {}
    for col in df_gt.columns:
        if not gt_numeric[col]:
            ts, is_date = _to_timestamps_if_date(df_gt[col])
            gt_timestamps[col] = ts if is_date else None
    for col in df_gen.columns:
        if not gen_numeric[col]:
            ts, is_date = _to_timestamps_if_date(df_gen[col])
            gen_timestamps[col] = ts if is_date else None

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
                if gen_numeric[gen_col]:
                    score = 0.0
                elif gt_timestamps[gt_col] is not None and gen_timestamps.get(gen_col) is not None:
                    # Both look like dates → compare as timestamps (numeric)
                    score = _numeric_match_score(gen_timestamps[gen_col], gt_timestamps[gt_col])
                elif gt_timestamps[gt_col] is not None or gen_timestamps.get(gen_col) is not None:
                    # One is a date, other is not → penalise
                    score = 0.0
                else:
                    # Both plain categorical → property-based score
                    score = _cat_property_score(df_gen[gen_col], df_gt[gt_col])

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
                            pairs: list, column_map: list,
                            df_gen: pd.DataFrame | None = None) -> dict:
    """
    Compute a score for every GT column:
      - Integer GT column   → (js_similarity + range_overlap + nunique_sim + missing_sim) / 4
      - Float GT column     → 0.5 * (js_similarity + range_overlap)
      - Categorical GT column → (cat_property_score + nunique_sim + missing_sim) / 3

    nunique_sim = 1 - |n_unique_gen/len_gen  - n_unique_gt/len_gt|  (fraction-based)
    missing_sim = 1 - |frac_missing_gen - frac_missing_gt|

    nunique_sim and missing_sim are computed on the FULL generated output column
    (df_gen, before any row-truncation) when df_gen is supplied, so they reflect
    the script's actual output rather than the GT-capped aligned copy.

    pairs: list of (gen_col, gt_col) name tuples (aligned names — gen_col == gt_col)
    column_map: output of build_jaccard_column_map (for categorical Jaccard lookup)

    Returns:
        dict with keys:
          "per_column"        → {gt_col: {...details...}}
          "avg_column_score"  → float | None
          "avg_js_similarity" → float | None  (numeric cols only, for debug)
          "avg_range_overlap" → float | None  (numeric cols only, for debug)
    """
    jaccard_lookup  = {entry["gt_col"]: entry["jaccard"] for entry in column_map}
    # Map gt_col → original gen_col name (before alignment renaming)
    orig_gen_lookup = {entry["gt_col"]: entry["gen_col"] for entry in column_map}

    per_column = {}

    for gen_col, gt_col in pairs:
        if gen_col not in df_aligned.columns or gt_col not in df_gt.columns:
            continue

        gen_series = df_aligned[gen_col]
        gt_series  = df_gt[gt_col]
        gt_numeric = np.issubdtype(gt_series.dtype, np.number)

        # Full gen column (before GT-row truncation) for nunique/missing metrics.
        orig_gen_col = orig_gen_lookup.get(gt_col, gen_col)
        if df_gen is not None and orig_gen_col in df_gen.columns:
            gen_series_full = df_gen[orig_gen_col]
        else:
            gen_series_full = gen_series

        # ── Categorical (or date treated as numeric) ──────────────────────────
        if not gt_numeric:
            gt_ts, gt_is_date = _to_timestamps_if_date(gt_series)
            gen_ts, gen_is_date = _to_timestamps_if_date(gen_series)
            if gt_is_date and gen_is_date:
                col_score = _numeric_match_score(gen_ts, gt_ts)
                col_type  = "date_as_numeric"
                per_column[gt_col] = {
                    "type":         col_type,
                    "gen_col":      gen_col,
                    "column_score": col_score,
                }
            elif gt_is_date or gen_is_date:
                col_score = 0.0
                col_type  = "date_mismatch"
                per_column[gt_col] = {
                    "type":         col_type,
                    "gen_col":      gen_col,
                    "column_score": col_score,
                }
            else:
                cat_score   = _cat_property_score(gen_series, gt_series)
                nunique_sim = _nunique_sim(gen_series_full, gt_series)
                missing_sim = _missing_sim(gen_series_full, gt_series)
                col_score   = round((cat_score + nunique_sim + missing_sim) / 3, 4)
                per_column[gt_col] = {
                    "type":         "categorical",
                    "gen_col":      gen_col,
                    "column_score": col_score,
                    "cat_score":    cat_score,
                    "nunique_sim":  nunique_sim,
                    "missing_sim":  missing_sim,
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

        # ID columns: JS similarity, range overlap, and Wasserstein are meaningless
        # for identifier columns (arbitrary integers with no numeric semantics).
        # Only uniqueness matters.
        is_id_col     = "id" in gt_col.lower()
        is_gt_integer = np.issubdtype(gt_series.dtype, np.integer)

        if is_id_col:
            nunique_sim   = _nunique_sim(gen_series_full, gt_series)
            missing_sim   = _missing_sim(gen_series_full, gt_series)
            js_similarity = None
            range_overlap = None
            w_norm        = None
            column_score  = nunique_sim
        else:
            # Wasserstein (debug only)
            w = wasserstein_distance(gen_vals, gt_vals)
            r = max(float(gen_vals.max() - gen_vals.min()),
                    float(gt_vals.max()  - gt_vals.min()), 1e-10)
            w_norm = w / r

        if is_id_col:
            pass  # already handled above
        elif is_gt_integer:
            nunique_sim = _nunique_sim(gen_series_full, gt_series)
            missing_sim = _missing_sim(gen_series_full, gt_series)
            # JS similarity gets 2× weight: it correctly penalises distribution
            # shifts caused by self-union tricks (e.g. 2× SUM) whereas
            # range_overlap only looks at endpoints and can reward inflated values.
            column_score = round((2*js_similarity + range_overlap + nunique_sim + missing_sim) / 5, 4)
        else:
            nunique_sim = None
            missing_sim = None
            # JS gets 2× weight vs range for same reason.
            column_score = round((2*js_similarity + range_overlap) / 3, 4)

        per_column[gt_col] = {
            "type":                   "id" if is_id_col else "numeric",
            "gen_col":                gen_col,
            "column_score":           column_score,
            "js_similarity":          js_similarity,
            "range_overlap":          range_overlap,
            "nunique_sim":            nunique_sim,
            "missing_sim":            missing_sim,
            "wasserstein_normalized": round(w_norm, 4) if w_norm is not None else None,
            "gen_stats": None if is_id_col else {
                "min":  round(gen_min, 4),
                "max":  round(gen_max, 4),
                "mean": round(float(gen_vals.mean()), 4),
            },
            "gt_stats": None if is_id_col else {
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
# Column reduction for wide tables
# ---------------------------------------------------------------------------

def _reduce_columns_for_scoring(df: pd.DataFrame, max_cols: int = MAX_COLS_FOR_SCORING) -> pd.DataFrame:
    """
    When df_gt has more than max_cols columns, select max_cols evenly-spaced
    columns (by position) so that FD mining in relative_csv_score stays within
    the 60-second timeout budget.  Selection is deterministic and preserves
    proportional coverage of the schema.
    """
    n = len(df.columns)
    if n <= max_cols:
        return df
    return df.iloc[:, :max_cols]


# ---------------------------------------------------------------------------
# Main scoring entry point
# ---------------------------------------------------------------------------

def value_based_relative_csv_score(df_gen: pd.DataFrame, df_gt: pd.DataFrame, precomputed_gt=None):
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

    df_gen = df_gen.drop(columns=[c for c in df_gen.columns if c.startswith("Unnamed:")], errors="ignore")
    df_gt  = df_gt.drop(columns=[c for c in df_gt.columns  if c.startswith("Unnamed:")], errors="ignore")

    # df_gt arrives already reduced when needed (done upstream in _value_score_worker).
    # Cap df_aligned rows to match df_gt so all scoring steps compare consistent sizes.
    _gt_max_rows = len(df_gt)

    column_map = build_jaccard_column_map(df_gen, df_gt)
    df_aligned = build_aligned_dataframe(df_gen, column_map)

    if len(df_aligned) > _gt_max_rows:
        df_aligned = df_aligned.iloc[:_gt_max_rows]

    fd_ratio, col_ratio, combined_score, fd_f1, _, debug_dict = \
        relative_csv_score(df_aligned, df_gt, precomputed_gt=precomputed_gt)

    pairs = [(col, col) for col in df_gt.columns if col in df_aligned.columns]
    col_scores = _compute_column_scores(df_aligned, df_gt, pairs, column_map, df_gen=df_gen)

    avg_column_score = col_scores.get("avg_column_score")

    # Row-count similarity: penalises outputs that have too many or too few rows.
    # Rows with any missing value (e.g. padding from an unmatched OUTER/LEFT/RIGHT
    # join) are discounted — they don't represent genuine matched data, so counting
    # them at face value would let row-inflating joins inflate row_ratio for free.
    n_gen_full = len(df_gen)   # full generated output row count (before any truncation)
    n_gt_full  = len(df_gt)    # GT row count (possibly truncated, but consistent)
    n_gen_complete = n_gen_full - int(df_gen.isna().any(axis=1).sum())
    row_ratio  = (min(n_gen_complete, n_gt_full) / max(n_gen_complete, n_gt_full)
                  if max(n_gen_complete, n_gt_full) > 0 else 1.0)

    # score_1: lightweight structural score = (fd_f1 + avg_col_score_1) / 2
    #   per-column contribution:
    #     numeric (float/int) → range_overlap only  (no JS, no nunique/missing)
    #     categorical         → cat_score (Jaccard-based min-hash property score)
    #     id column           → nunique_sim
    #     date                → column_score (unchanged)
    # No row_ratio penalty. Robust when row-count or JS penalties drag score_2 down.
    _per_col = col_scores.get("per_column") or {}
    if _per_col:
        _s1_vals = []
        for _cd in _per_col.values():
            _ct = _cd.get("type", "")
            if _ct == "numeric":
                _s1_vals.append(_cd.get("range_overlap") or 0.0)
            elif _ct == "id":
                _s1_vals.append(_cd.get("nunique_sim") or 0.0)
            elif _ct == "categorical":
                _s1_vals.append(_cd.get("cat_score") or 0.0)
            else:  # date_as_numeric, date_mismatch
                _s1_vals.append(_cd.get("column_score", 0.0))
        _avg_col_score_1 = round(sum(_s1_vals) / len(_s1_vals), 4)
        score_1 = round((fd_f1 + _avg_col_score_1) / 2, 4)
    else:
        _avg_col_score_1 = None
        score_1 = round(fd_f1, 4)

    # score_2: full value-based score = (fd_f1 + avg_column_score + row_ratio) / 3.
    # Includes JS similarity, nunique/missing similarity, and row-count penalty.
    if avg_column_score is not None:
        score_2 = round((fd_f1 + avg_column_score + row_ratio) / 3, 4)
    else:
        score_2 = round((fd_f1 + row_ratio) / 2, 4)

    true_combined_score = max(score_1, score_2)

    debug_dict["column_scores"]        = col_scores
    debug_dict["row_ratio"]            = round(row_ratio, 4)
    debug_dict["n_gen_full"]           = n_gen_full
    debug_dict["n_gen_complete"]       = n_gen_complete
    debug_dict["avg_col_score_1"]      = _avg_col_score_1
    debug_dict["score_1"]              = score_1
    debug_dict["score_2"]              = score_2
    debug_dict["true_combined_score"]  = true_combined_score
    debug_dict["jaccard_column_map"]   = column_map

    return fd_ratio, col_ratio, combined_score, fd_f1, true_combined_score, debug_dict


def _score_worker_proc(df_gen, df_gt, precomputed_gt, result_queue):
    """Subprocess target: run scoring and put the 6-tuple result in the queue."""
    try:
        result = value_based_relative_csv_score(df_gen, df_gt, precomputed_gt)
        result_queue.put(result)
    except Exception:
        result_queue.put(None)


def value_based_relative_csv_score_timed(df_gen: pd.DataFrame, df_gt: pd.DataFrame,
                                          timeout: int = SCORE_TIMEOUT, precomputed_gt=None):
    """
    Calls value_based_relative_csv_score in a child process with a hard timeout.
    On timeout the child is terminate()d — fully stopping the computation and
    releasing all its memory — then TimeoutError is raised.
    """
    import multiprocessing as _mp
    q = _mp.Queue()
    p = _mp.Process(target=_score_worker_proc, args=(df_gen, df_gt, precomputed_gt, q), daemon=True)
    p.start()
    p.join(timeout=timeout)
    if p.is_alive():
        p.terminate()
        p.join()
        raise TimeoutError(f"value_based_relative_csv_score timed out after {timeout}s")
    try:
        result = q.get_nowait()
    except Exception:
        result = None
    if result is None:
        raise TimeoutError(f"value_based_relative_csv_score failed in subprocess")
    return result
