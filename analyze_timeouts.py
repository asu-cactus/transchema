#!/usr/bin/env python3
"""
analyze_timeouts.py — For each timeout case, extract the last Python script
from the most recent log file, execute it, and run autopipeline validation
using compare_tables from validation/autopipeline_match.py.

Timeout cases: 4_30, 4_36, 4_37, 4_38, 4_71
Log directory: logs_langraph/mcts_l4_score_pipeline_static
Results run  : mcts_l4_score_pipeline_static_20260428_193300
"""

import os
import re
import sys
import glob
import tempfile
import subprocess

import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(ROOT, "logs_langraph", "mcts_l4_score_pipeline_static")
BENCHMARK_DIR = os.path.join(ROOT, "autopipeline-benchmarks", "github-pipelines")

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from validation.autopipeline_match import compare_tables

TIMEOUT_CASES = ["4_30", "4_36", "4_37", "4_38", "4_71"]

PYTHON_BIN = os.path.join(ROOT, "env", "bin", "python3")
if not os.path.exists(PYTHON_BIN):
    PYTHON_BIN = sys.executable


def get_case_number(case_id):
    """Convert '4_30' -> '30'."""
    return case_id.split("_")[1]


def find_latest_log(case_id):
    """Return the most recent log file for the given case id."""
    n = get_case_number(case_id)
    pattern = os.path.join(LOG_DIR, f"4_target{n}_MCTS_*.log")
    files = glob.glob(pattern)
    if not files:
        return None
    # Filenames embed timestamp, so lexicographic sort gives chronological order
    return sorted(files)[-1]


def extract_all_python_blocks(log_path):
    """Extract all ```Python ... ``` blocks from a log file."""
    with open(log_path, "r", errors="replace") as f:
        content = f.read()

    blocks = re.findall(r"```[Pp]ython\s*\n(.*?)```", content, re.DOTALL)
    return [b.strip() for b in blocks]


def run_pipeline_script(case_id, code):
    """Write code to a temp file and execute it from the project root."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=f"_{case_id}.py",
        delete=False,
        dir=ROOT,
        prefix="tmp_pipeline_",
    )
    tmp.write(code)
    tmp.close()

    print(f"  [run] Executing: {os.path.basename(tmp.name)}")
    result = subprocess.run(
        [PYTHON_BIN, tmp.name],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    os.unlink(tmp.name)

    if result.returncode != 0:
        print(f"  [run] FAILED (exit {result.returncode})")
        if result.stderr.strip():
            for line in result.stderr.strip().splitlines():
                print(f"    {line}")
    else:
        print(f"  [run] OK")

    return result.returncode == 0


def run_validation(case_id):
    """Run compare_tables validation between generated and ground truth CSVs."""
    case_dir = os.path.join(BENCHMARK_DIR, f"length{case_id}")
    gen_path = os.path.join(case_dir, "target_multisource_mcts.csv")
    gt_path = os.path.join(case_dir, "target.csv")

    if not os.path.exists(gen_path):
        print(f"  [validate] Generated CSV not found: {gen_path}")
        return
    if not os.path.exists(gt_path):
        print(f"  [validate] Ground truth CSV not found: {gt_path}")
        return

    df_gen = pd.read_csv(gen_path, low_memory=False)
    df_gt = pd.read_csv(gt_path, low_memory=False)
    # target.csv has a leading index column — drop it
    df_gt = df_gt.drop(columns=df_gt.columns[0])

    print(f"  [validate] gen shape: {df_gen.shape}, gt shape: {df_gt.shape}")

    is_correct, matched_cols = compare_tables(df_gen, df_gt)

    print(f"  [validate] is_correct  : {is_correct}")
    if matched_cols:
        print(f"  [validate] matched_cols: {matched_cols}")


def main():
    for case_id in TIMEOUT_CASES:
        print("=" * 70)
        print(f"CASE {case_id}")
        print("=" * 70)

        log_path = find_latest_log(case_id)
        if log_path is None:
            print(f"  No log file found for {case_id} in {LOG_DIR}")
            continue
        print(f"  Log : {os.path.basename(log_path)}")

        blocks = extract_all_python_blocks(log_path)
        if not blocks:
            print(f"  No Python code blocks found in log.")
            continue
        print(f"  Found {len(blocks)} Python block(s)\n")

        for i, code in enumerate(blocks, 1):
            print(f"  --- Block {i}/{len(blocks)} ({len(code.splitlines())} lines) ---")
            success = run_pipeline_script(case_id, code)
            if success:
                run_validation(case_id)
            print()

        print()


if __name__ == "__main__":
    main()
