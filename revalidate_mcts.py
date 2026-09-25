"""
revalidate_mcts.py

For each length{LENGTH}_* case that has a python_recovered_mcts.py:
  1. Run the script (writes target_multisource_mcts.csv)
  2. Validate against target.csv using autopipeline's compare_tables
  3. Write results to revalidate_mcts_results.csv

Run from the project root:
    python revalidate_mcts.py --length 4
    python revalidate_mcts.py --length 9
    python revalidate_mcts.py --length 4 9   # both at once
"""

import argparse
import csv
import os
import subprocess
import sys
import traceback

import pandas as pd

from validation.autopipeline_match import compare_tables

BENCHMARKS_DIR = "autopipeline-benchmarks/github-pipelines"
SCRIPT_NAME = "python_recovered_mcts.py"
OUTPUT_CSV = "target_multisource_mcts.csv"
TARGET_CSV = "target.csv"


def run_case(case_dir: str) -> dict:
    script_path = os.path.join(case_dir, SCRIPT_NAME)
    output_path = os.path.join(case_dir, OUTPUT_CSV)
    target_path = os.path.join(case_dir, TARGET_CSV)
    case_id = os.path.basename(case_dir)

    result = {
        "case_id": case_id,
        "is_correct": False,
        "matched_columns": "",
        "status": "error",
        "error": "",
    }

    # --- Run the script ---
    try:
        proc = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if proc.returncode != 0:
            result["error"] = proc.stderr.strip().splitlines()[-1] if proc.stderr else "non-zero exit"
            return result
    except subprocess.TimeoutExpired:
        result["error"] = "timeout"
        return result
    except Exception as e:
        result["error"] = str(e)
        return result

    # --- Load output and ground truth ---
    try:
        df_output = pd.read_csv(output_path, low_memory=False)
    except Exception as e:
        result["error"] = f"cannot read output csv: {e}"
        return result

    try:
        df_gt = pd.read_csv(target_path, low_memory=False)
        # drop index column if present
        if df_gt.columns[0].startswith("Unnamed"):
            df_gt = df_gt.drop(columns=df_gt.columns[0])
    except Exception as e:
        result["error"] = f"cannot read target csv: {e}"
        return result

    # --- Validate ---
    try:
        is_correct, matched_columns = compare_tables(df_output, df_gt)
        result["is_correct"] = is_correct
        result["matched_columns"] = str(matched_columns)
        result["status"] = "correct" if is_correct else "incorrect"
    except Exception as e:
        result["error"] = f"validation failed: {e}\n{traceback.format_exc()}"

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--length",
        type=int,
        nargs="+",
        default=[4],
        help="Length bucket(s) to revalidate, e.g. --length 4 9",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="revalidate_mcts_results.csv",
        help="Path for the results CSV",
    )
    args = parser.parse_args()

    # Collect all matching case dirs
    all_cases = sorted(os.listdir(BENCHMARKS_DIR))
    prefixes = tuple(f"length{l}_" for l in args.length)
    cases = [
        os.path.join(BENCHMARKS_DIR, c)
        for c in all_cases
        if c.startswith(prefixes) and os.path.isfile(os.path.join(BENCHMARKS_DIR, c, SCRIPT_NAME))
    ]

    print(f"Found {len(cases)} case(s) with {SCRIPT_NAME} for length(s) {args.length}\n")

    fields = ["case_id", "is_correct", "matched_columns", "status", "error"]
    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        correct = 0
        for i, case_dir in enumerate(cases, 1):
            case_id = os.path.basename(case_dir)
            print(f"[{i}/{len(cases)}] {case_id} ...", end=" ", flush=True)
            result = run_case(case_dir)
            writer.writerow(result)
            f.flush()
            icon = "✓" if result["is_correct"] else ("✗" if result["status"] != "error" else "!")
            print(f"{icon}  {result['status']}" + (f"  — {result['error']}" if result["error"] else ""))
            if result["is_correct"]:
                correct += 1

    total = len(cases)
    print(f"\nDone. {correct}/{total} correct ({100*correct/total:.1f}%)")
    print(f"Results saved to: {args.output}")


if __name__ == "__main__":
    main()
