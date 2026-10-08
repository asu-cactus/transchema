"""
collect_scraped_script_scores_exact_align.py
================================================
Identical collection pipeline to collect_scraped_script_scores.py, but with a
different column alignment strategy.

Motivation: build_jaccard_column_map (used by value_based_relative_csv_score)
aligns columns via fuzzy heuristics -- JS-similarity/range-overlap for
numeric columns, structural string-shape properties for categorical columns
-- which can coincidentally mismatch two unrelated columns that just happen
to look statistically similar (acknowledged in build_jaccard_column_map's own
docstring). validation/autopipeline_match.py's compare_tables(), which
actually decides is_match, uses a much stricter primitive: compare_series,
genuine value-level equality (same row count after dropna, numeric values
equal within 10% after sorting, non-numeric values equal exactly). That's the
real ground truth for "these two columns are the same data."

compare_tables itself can't be reused directly as an alignment source: its
column loop exits with (False, []) -- discarding every match already found,
not just the unmatched column -- the instant ANY target column fails to find
an exact match, so it only ever returns a mapping when the whole table
matches exactly. 83% of scraped scripts don't (is_match=False), so
compare_tables's own output has no mapping to reuse for most of the dataset.

This script instead drives compare_series itself, per (gt_col, gen_col) pair,
independent of that early-exit behavior: for each GT column, prefer an exact
value-level match (compare_series) over the fuzzy heuristic, and only fall
back to the fuzzy heuristic for GT columns where no gen column matches
exactly. Every script gets a full alignment, with the trustworthy signal
taking priority wherever it's available.

Implementation: monkey-patches eval_score_value_based.build_jaccard_column_map
before collect_scraped_script_scores is imported. value_based_relative_csv_score
resolves build_jaccard_column_map via its module's globals at call time (not
at def time), so every downstream function -- value_based_relative_csv_score,
relative_csv_score, _compute_column_scores -- is reused completely unchanged;
only the alignment step differs. No codebase files are modified.

Usage:  python3 collect_scraped_script_scores_exact_align.py [--lengths 1 2 3 4 5 9] [--workers 20] [--cases_per_length N]
Output: scraped_scripts/scraped_scripts_scores_exact_align.csv
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent
if str(WORK_DIR) not in sys.path:
    sys.path.insert(0, str(WORK_DIR))

import eval_score_value_based as evb
from validation.autopipeline_match import compare_series

_fuzzy_build_jaccard_column_map = evb.build_jaccard_column_map


def _find_exact_match(gt_series, df_gen):
    """First gen column whose values exactly match gt_series via
    compare_series -- the same strict value-equality primitive
    validation/autopipeline_match.compare_tables() itself trusts to decide
    is_match. Returns None if no gen column matches exactly."""
    for gen_col in df_gen.columns:
        try:
            if compare_series(gt_series, df_gen[gen_col]):
                return gen_col
        except Exception:
            continue
    return None


def build_exact_then_fuzzy_column_map(df_gen, df_gt):
    """Drop-in replacement for build_jaccard_column_map: exact value-level
    match first (compare_series), fuzzy heuristic fallback only for GT
    columns where no gen column matches exactly. Same return shape as the
    original -- list of {"gt_col", "gen_col", "jaccard"} dicts, ordered by
    df_gt.columns -- with an extra "exact_match" bool per entry so it's
    visible downstream in debug_dict["jaccard_column_map"]."""
    fuzzy_map = _fuzzy_build_jaccard_column_map(df_gen, df_gt)
    patched = []
    for entry in fuzzy_map:
        gt_col = entry["gt_col"]
        exact_gen_col = _find_exact_match(df_gt[gt_col], df_gen)
        if exact_gen_col is not None:
            patched.append({
                "gt_col": gt_col, "gen_col": exact_gen_col,
                "jaccard": 1.0, "exact_match": True,
            })
        else:
            patched.append({**entry, "exact_match": False})
    return patched


# Patch BEFORE importing the collector -- value_based_relative_csv_score looks
# up build_jaccard_column_map through eval_score_value_based's own globals at
# call time, so every call it makes from here on uses the patched version.
evb.build_jaccard_column_map = build_exact_then_fuzzy_column_map

import collect_scraped_script_scores as base  # noqa: E402  (must follow the patch)

base.DEFAULT_OUTPUT = base.SCRAPED_DIR / "scraped_scripts_scores_exact_align.csv"

if __name__ == "__main__":
    base.main()
