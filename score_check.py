#!/usr/bin/env python3
"""
score_check.py — compute eval_score and validation between two CSV files.

Usage:
    python score_check.py <generated_csv> <ground_truth_csv>
    python score_check.py <generated_csv> <ground_truth_csv> --validation autopipeline
    python score_check.py <generated_csv> <ground_truth_csv> --validation hard_match
    python score_check.py <generated_csv> <ground_truth_csv> --json

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


def main():
    parser = argparse.ArgumentParser(description="Score a generated CSV against a ground truth CSV.")
    parser.add_argument("generated", help="Path to the generated output CSV")
    parser.add_argument("ground_truth", help="Path to the ground truth CSV (first column is dropped as index)")
    parser.add_argument("--no-drop-index", action="store_true",
                        help="Skip dropping the first column of ground truth (if it has no index column)")
    parser.add_argument("--validation", choices=["autopipeline", "hard_match", "none"], default="autopipeline",
                        help="Validation mode: 'autopipeline' (default), 'hard_match', or 'none'")
    parser.add_argument("--json", action="store_true", help="Print full debug JSON instead of summary")
    args = parser.parse_args()

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
        print("=" * 60)
        print()

    if args.json:
        print("Full debug JSON:")
        print(json.dumps(debug_dict, indent=2))


if __name__ == "__main__":
    main()
