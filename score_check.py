#!/usr/bin/env python3
"""
score_check.py — compute eval_score and validation between two CSV files.

Usage:
    python score_check.py <generated_csv> <ground_truth_csv>
    python score_check.py <generated_csv> <ground_truth_csv> --validation autopipeline
    python score_check.py <generated_csv> <ground_truth_csv> --validation hard_match
    python score_check.py <generated_csv> <ground_truth_csv> --json

    # Batch mode: scan a list of cases for autopipeline column-name mismatches
    python score_check.py --batch --cases 4_26 4_30 4_34 ...
    python score_check.py --batch --cases 4_26 4_30 --benchmark-dir autopipeline-benchmarks/github-pipelines
    python score_check.py --batch --cases 4_26 4_30 --generated-suffix _multisource_mcts

The ground truth CSV is expected to have a leading index column (as produced
by pandas to_csv()), which is automatically dropped before scoring — matching
the same pre-processing done inside the MCTS pipeline.
"""

import sys
import os
import json
import argparse

import pandas as pd

# Resolve project root so eval_score and validation are importable regardless of cwd
_ROOT = os.path.dirname(os.path.abspath(__file__))
_EVAL_SCORE = os.path.join(_ROOT, "eval_score")
for p in (_ROOT, _EVAL_SCORE):
    if p not in sys.path:
        sys.path.insert(0, p)

from eval_score.score import relative_csv_score, summarize_score
from validation.hard_match import compare_tables_matching, compare_lists_matching
from validation.autopipeline_match import compare_series


def _cols_have_same_data(df, col_a, col_b):
    """Return True if two columns in df have identical sorted values (order-independent)."""
    try:
        a = df[col_a].dropna().sort_values().reset_index(drop=True)
        b = df[col_b].dropna().sort_values().reset_index(drop=True)
        return a.equals(b)
    except Exception:
        return False


def _is_degenerate_mismatch(tgt_col, gen_col, df_gen, df_gt):
    """A mismatch is degenerate (false positive) in three sub-cases:
      1. Correct column exists with right data — df_gen[tgt_col] matches df_gt[tgt_col]
         via compare_series; the matcher picked a different column first due to loose
         tolerance or duplicate values (e.g. 4_26, 4_77).
      2. Duplicate column names — pandas renamed duplicates with .1/.2 suffixes; the
         correctly-named column still exists and its data matches the target.
      3. Same-data duplicate — tgt_col exists in df_gen with the same data as the
         wrongly-matched gen_col (ambiguous content, matcher picked wrong name first).
    Any case where tgt_col exists but its data does not match the target is real."""
    if tgt_col not in df_gen.columns:
        return False
    # Sub-case 1 & 2: correctly-named column data matches the target column
    try:
        if compare_series(df_gt[tgt_col], df_gen[tgt_col]):
            return True
    except Exception:
        pass
    # Sub-case 3: correctly-named column has same data as the wrongly-matched column
    return _cols_have_same_data(df_gen, tgt_col, gen_col)


def run_batch(cases, benchmark_dir, generated_suffix):
    """Check autopipeline column-name mismatches across multiple cases."""
    mismatched_cases = []

    for case in cases:
        case_dir = os.path.join(_ROOT, benchmark_dir, f"length{case}")
        gt_path  = os.path.join(case_dir, "target.csv")
        gen_path = os.path.join(case_dir, f"target{generated_suffix}.csv")

        if not os.path.exists(gt_path):
            print(f"[{case}] SKIP — target.csv not found: {gt_path}")
            continue
        if not os.path.exists(gen_path):
            print(f"[{case}] SKIP — generated CSV not found: {gen_path}")
            continue

        df_gen = pd.read_csv(gen_path, low_memory=False)
        df_gt  = pd.read_csv(gt_path, low_memory=False)
        # target.csv has a leading index column
        df_gt  = df_gt.drop(columns=df_gt.columns[0], axis=1)

        avg_sim, is_correct, col_sims, matched_cols = compare_tables_matching(df_gen, df_gt)

        if not is_correct or not matched_cols:
            print(f"[{case}] SKIP — validation failed (is_correct={is_correct}), not analysing column names")
            continue

        all_mismatches = [
            (tgt, gen)
            for tgt, gen in zip(df_gt.columns, matched_cols)
            if tgt != gen
        ]

        # Split into real mismatches vs degenerate (duplicate-data) false positives
        real_mismatches      = [(t, g) for t, g in all_mismatches if not _is_degenerate_mismatch(t, g, df_gen, df_gt)]
        degenerate_mismatches = [(t, g) for t, g in all_mismatches if     _is_degenerate_mismatch(t, g, df_gen, df_gt)]

        if real_mismatches:
            print(f"[{case}] NAME MISMATCHES ({len(real_mismatches)}/{len(df_gt.columns)} cols):")
            for tgt, gen in real_mismatches:
                print(f"         target {tgt!r:40s} → generated {gen!r}")
            if degenerate_mismatches:
                print(f"         (+ {len(degenerate_mismatches)} degenerate/duplicate-data mismatches filtered out)")
            mismatched_cases.append(case)
        elif degenerate_mismatches:
            print(f"[{case}] OK (degenerate) — {len(degenerate_mismatches)} apparent mismatch(es) filtered: "
                  f"correct column name exists with identical data")
        else:
            print(f"[{case}] OK — all {len(df_gt.columns)} column names match")

    print()
    print("=" * 60)
    print(f"Cases with column-name mismatches ({len(mismatched_cases)}/{len(cases)}):")
    for c in mismatched_cases:
        print(f"  {c}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Score a generated CSV against a ground truth CSV.")
    parser.add_argument("generated", nargs="?", help="Path to the generated output CSV")
    parser.add_argument("ground_truth", nargs="?", help="Path to the ground truth CSV (first column is dropped as index)")
    parser.add_argument("--no-drop-index", action="store_true",
                        help="Skip dropping the first column of ground truth (if it has no index column)")
    parser.add_argument("--validation", choices=["autopipeline", "hard_match", "none"], default="autopipeline",
                        help="Validation mode: 'autopipeline' (default), 'hard_match', or 'none'")
    parser.add_argument("--json", action="store_true", help="Print full debug JSON instead of summary")
    # Batch mode
    parser.add_argument("--batch", action="store_true",
                        help="Batch mode: scan cases for autopipeline column-name mismatches")
    parser.add_argument("--cases", nargs="+", metavar="CASE",
                        help="Case IDs to check in batch mode, e.g. 4_26 4_30 4_34")
    parser.add_argument("--benchmark-dir", default="autopipeline-benchmarks/github-pipelines",
                        help="Benchmark directory relative to project root (default: autopipeline-benchmarks/github-pipelines)")
    parser.add_argument("--generated-suffix", default="_multisource_mcts",
                        help="Suffix for generated CSV filename: target<suffix>.csv (default: _multisource_mcts)")
    args = parser.parse_args()

    if args.batch:
        if not args.cases:
            parser.error("--batch requires --cases")
        run_batch(args.cases, args.benchmark_dir, args.generated_suffix)
        return

    df_gen = pd.read_csv(args.generated, low_memory=False)
    df_gt  = pd.read_csv(args.ground_truth, low_memory=False)

    if not args.no_drop_index:
        df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)

    print(f"Generated shape : {df_gen.shape}  columns: {list(df_gen.columns)}")
    print(f"Ground truth shape: {df_gt.shape}  columns: {list(df_gt.columns)}")
    print()

    fd_ratio, col_ratio, combined_score, fd_f1, true_combined_score, debug_dict = relative_csv_score(df_gen, df_gt)

    # This is exactly the score the MCTS pipeline uses
    pipeline_score = (fd_f1 + col_ratio) / 2

    summary = summarize_score(debug_dict, pipeline_score, fd_f1, col_ratio)

    print("=" * 60)
    print(f"  Pipeline score (fd_f1 + col_ratio) / 2  : {pipeline_score:.4f}")
    print(f"  FD F1                                    : {fd_f1:.4f}")
    print(f"  Column ratio                             : {col_ratio:.4f}")
    print(f"  True combined (fd_f1 + col + dist) / 3  : {true_combined_score:.4f}")
    print("=" * 60)
    print()

    dist = debug_dict.get("distribution", {})
    dist_sim = dist.get("avg_distribution_similarity")
    if dist_sim is not None:
        print(f"  Avg distribution similarity (Wasserstein): {dist_sim:.4f}")
        for col, info in dist.get("per_column", {}).items():
            print(f"    {col}: similarity={info['distribution_similarity']:.4f}  "
                  f"gen_mean={info['gen_stats']['mean']}  gt_mean={info['gt_stats']['mean']}")
        print()

    print("Column mapping:")
    print(f"  Matched {summary['column_mappings']['matched_count']} / "
          f"{summary['column_mappings']['total_target_columns']} ground-truth columns")
    if summary["column_mappings"]["missed_target_columns"]:
        print(f"  Missed columns: {summary['column_mappings']['missed_target_columns']}")
    print()

    print("Functional dependencies:")
    print(f"  Ground truth FD count : {summary['functional_dependencies']['ground_truth_count']}")
    print(f"  Generated FD count    : {summary['functional_dependencies']['output_count']}")
    if summary["functional_dependencies"]["missed"]:
        print(f"  Missed FDs : {summary['functional_dependencies']['missed']}")
    if summary["functional_dependencies"]["unexpected"]:
        print(f"  Extra FDs  : {summary['functional_dependencies']['unexpected']}")
    print()

    if args.validation != "none":
        validate_fn = compare_tables_matching if args.validation == "autopipeline" else compare_lists_matching
        avg_sim, is_correct, col_sims, matched_cols = validate_fn(df_gen, df_gt)
        print("=" * 60)
        print(f"  Validation ({args.validation})")
        print(f"  is_correct       : {is_correct}")
        print(f"  avg_similarity   : {avg_sim:.4f}")
        print(f"  matched_cols     : {matched_cols}")
        if args.validation == "autopipeline" and matched_cols:
            print()
            print("  Column matching (target → generated):")
            for tgt_col, gen_col in zip(df_gt.columns, matched_cols):
                match_marker = "" if tgt_col == gen_col else "  *** NAME MISMATCH ***"
                print(f"    {tgt_col!r:40s} → {gen_col!r}{match_marker}")
        print("=" * 60)
        print()

    if args.json:
        print("Full debug JSON:")
        print(json.dumps(debug_dict, indent=2))


if __name__ == "__main__":
    main()
