#!/usr/bin/env python3
"""
find_duplicate_columns.py — find target.csv files where any two columns share identical data.

Usage:
    python find_duplicate_columns.py                    # L1, L4, L9 (default)
    python find_duplicate_columns.py --lengths 1 4
    python find_duplicate_columns.py --benchmark-dir autopipeline-benchmarks/github-pipelines
"""

import os
import sys
import argparse
import itertools

import pandas as pd

_ROOT = os.path.dirname(os.path.abspath(__file__))


def cols_are_identical(s1, s2):
    """True if two Series have the same sorted values (order-independent, exact match)."""
    try:
        a = s1.dropna().sort_values().reset_index(drop=True)
        b = s2.dropna().sort_values().reset_index(drop=True)
        return a.equals(b)
    except Exception:
        return False


def check_length(length, benchmark_dir, filter_cases=None):
    """filter_cases: if given, a set of case suffixes like {'4_26', '4_30'} to restrict to."""
    prefix = f"length{length}_"
    base = os.path.join(_ROOT, benchmark_dir)
    cases = sorted(
        d for d in os.listdir(base)
        if d.startswith(prefix) and os.path.isdir(os.path.join(base, d))
    )
    if filter_cases is not None:
        cases = [d for d in cases if d[len(prefix)-2:] in filter_cases
                 or d.replace("length", "") in filter_cases]

    total = 0
    dup_cases = []

    for case in cases:
        target_path = os.path.join(base, case, "target.csv")
        if not os.path.exists(target_path):
            continue
        total += 1

        df = pd.read_csv(target_path, low_memory=False)
        # Drop the leading index column that target.csv always has
        df = df.drop(columns=df.columns[0], axis=1)

        dup_pairs = []
        cols = df.columns.tolist()
        for c1, c2 in itertools.combinations(cols, 2):
            if cols_are_identical(df[c1], df[c2]):
                dup_pairs.append((c1, c2))

        if dup_pairs:
            dup_cases.append((case, dup_pairs))

    print(f"\n{'=' * 60}")
    header = f"  Length {length}  —  {len(dup_cases)} / {total} cases have duplicate-data columns"
    if filter_cases is not None:
        header += f"  (filtered to {total} experiment cases)"
    print(header)
    print(f"{'=' * 60}")
    for case, _ in dup_cases:
        print(f"  {case}")

    return len(dup_cases), total, {c for c, _ in dup_cases}


EXPERIMENT_CASES_L4 = {
    "4_26", "4_27", "4_30", "4_31", "4_33", "4_34", "4_35", "4_36", "4_37", "4_38",
    "4_39", "4_40", "4_41", "4_42", "4_44", "4_59", "4_65", "4_71", "4_72", "4_74",
    "4_76", "4_77", "4_80", "4_81", "4_82", "4_85", "4_88", "4_89", "4_95", "4_97",
}


def main():
    parser = argparse.ArgumentParser(description="Find target CSVs with duplicate-data columns.")
    parser.add_argument("--lengths", nargs="+", type=int, default=[1, 4, 9],
                        help="Pipeline lengths to check (default: 1 4 9)")
    parser.add_argument("--benchmark-dir", default="autopipeline-benchmarks/github-pipelines",
                        help="Benchmark directory relative to project root")
    parser.add_argument("--experiment-overlap", action="store_true",
                        help="Also show overlap with the 30-case L4 experiment set")
    args = parser.parse_args()

    summary = []
    for length in args.lengths:
        dup_count, total, dup_set = check_length(length, args.benchmark_dir)
        summary.append((length, dup_count, total, dup_set))

    print(f"\n{'=' * 60}")
    print("  SUMMARY")
    print(f"{'=' * 60}")
    for length, dup_count, total, _ in summary:
        print(f"  L{length}: {dup_count} / {total} cases  ({100*dup_count/total:.1f}%)")
    print(f"{'=' * 60}")

    if args.experiment_overlap:
        for length, dup_count, total, dup_set in summary:
            if length != 4:
                continue
            # Normalise dup_set to bare IDs like "4_26"
            dup_ids = {d.replace("length", "") for d in dup_set}
            overlap = EXPERIMENT_CASES_L4 & dup_ids
            unaffected = EXPERIMENT_CASES_L4 - dup_ids
            print(f"\n{'=' * 60}")
            print(f"  30-case experiment overlap (L{length})")
            print(f"{'=' * 60}")
            print(f"  Cases WITH duplicate-data columns : {len(overlap)} / {len(EXPERIMENT_CASES_L4)}")
            for c in sorted(overlap):
                print(f"    {c}")
            print(f"  Cases WITHOUT duplicate-data columns: {len(unaffected)} / {len(EXPERIMENT_CASES_L4)}")
            print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
