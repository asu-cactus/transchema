"""
build_score_regression_dataset.py
====================================
Builds the regression dataset for finding weights of the 4 score_1 components
in eval_score_value_based.value_based_relative_csv_score:
  fd_f1, avg_col_score_1 (per-column), row_count_score, max_missing_score.

For every case in L1/L4/L9 (run9 training split for L1, test_script_4_l4/l9
for L4/L9), extracts every unique Python script seen anywhere in the MCTS log
(sim + critique turns, all iterations), and for each one runs TWO variants:

  1. TRAIN run (script as-is, reads training_N.csv): scores it with
     value_based_relative_csv_score against target.csv to get the 4 score_1
     components (fd_f1, avg_col_score_1, row_count_score, max_missing_score)
     plus score_1/score_2/row_ratio — this mirrors how MCTS itself computes
     reward during search (on the training split).
  2. TEST run (training_N.csv -> test_N.csv swapped): validated against
     target.csv with compare_tables_matching (binary correctness label) and
     compare_tables_fuzzy (continuous "partial reward" = matched/total
     column ratio) — this is the held-out generalization signal the
     regression will try to predict/maximize.

Parallelization: one task per (case, unique script) pair, dispatched to a
flat process pool (default 30 workers) — as soon as a worker frees up it
picks up the next script, regardless of which case it belongs to. Scripts
from the same case all hardcode the same output filename
(target_multisource_mcts.csv), so each run rewrites its script to write to
a unique per-run filename before executing, avoiding races between
concurrent scripts of the same case; temp output files are deleted after
scoring.

Usage:
  python3 build_score_regression_dataset.py [--cases_per_length N] [--lengths 1 4 9] [--workers 30]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import io
import csv
import glob
import uuid
import argparse
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

import pandas as pd
from tqdm import tqdm

from analyze_run8_failed_case_scripts import extract_all_scored_scripts
from eval_run8_training import run_script, swap_training_to_test
from validation.hard_match import compare_tables_matching
from validation.fuzzy_match import compare_tables_fuzzy
from eval_score_value_based import value_based_relative_csv_score

WORK_DIR = Path(".").resolve()
OUTPUT_BASENAME = "target_multisource_mcts.csv"

CONFIGS = [
    (1, "logs_langraph/rag_det_score_run9_l1_pilot20", list(range(20))),
    (1, "logs_langraph/rag_det_score_run9_l1_batch_20to100", list(range(20, 100))),
    (4, "logs_langraph/test_script_4_l4", list(range(100))),
    (9, "logs_langraph/test_script_4_l9", list(range(101))),
]

FIELDNAMES = [
    "length", "case_num", "iter", "kind", "log_score",
    # train-side: score_1 components (reward as MCTS would compute it)
    "train_run_ok", "train_error",
    "fd_f1", "avg_col_score_1", "row_count_score", "max_missing_score",
    "score_1", "score_2", "row_ratio", "true_combined_score",
    # test-side: held-out generalization signal
    "test_run_ok", "test_error",
    "is_match", "partial_reward",
]


# ---------------------------------------------------------------------------
# Extraction (fast, runs in main process — no script execution here)
# ---------------------------------------------------------------------------

def collect_tasks(lengths, cases_per_length=None):
    """Parse all logs and return a flat list of
    (length, case_num, iter, kind, script, log_score) — one per unique SCORE
    (rounded to 4dp), not per unique script text. Many distinct script texts
    land on the same score (trivial rewrites, equivalent op orderings on this
    data, etc.); the first script seen at a given score is kept as its
    representative, matching extract_unique_scored_scripts.py's definition."""
    tasks = []
    for length, log_dir, cases in CONFIGS:
        if length not in lengths:
            continue
        if cases_per_length is not None:
            cases = cases[:cases_per_length]
        for case_num in cases:
            files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
            if not files:
                continue
            log_file = Path(files[-1])  # latest timestamp when multiple exist
            entries = extract_all_scored_scripts(log_file)
            if not entries:
                continue
            seen = {}
            for it, kind, script, log_score in entries:
                key = round(log_score, 4)
                if key not in seen:
                    seen[key] = (it, kind, script, log_score)
            for it, kind, script, log_score in seen.values():
                tasks.append((length, case_num, it, kind, script, log_score))
    return tasks


# ---------------------------------------------------------------------------
# Per-script worker (runs in subprocess)
# ---------------------------------------------------------------------------

def _run_variant(script: str, case_dir: Path, gt_path: Path, tag: str):
    """Run one script variant to a unique output filename, return (ok, error, output_path)."""
    unique_name = f"target_multisource_mcts_{tag}_{uuid.uuid4().hex[:12]}.csv"
    if OUTPUT_BASENAME not in script:
        return False, "no_standard_output_filename_in_script", None
    rewritten = script.replace(OUTPUT_BASENAME, unique_name)
    output_path = case_dir / unique_name
    ok, err = run_script(rewritten, WORK_DIR)
    if not ok:
        return False, err[:150], output_path
    if not output_path.exists() or not gt_path.exists():
        return False, "missing_output_or_gt", output_path
    return True, "", output_path


def process_script(task) -> dict:
    length, case_num, it, kind, script, log_score = task
    row = {
        "length": length, "case_num": case_num, "iter": it,
        "kind": kind, "log_score": log_score,
    }

    case_dir = WORK_DIR / f"autopipeline-benchmarks/github-pipelines/length{length}_{case_num}"
    gt_path = case_dir / "target.csv"

    train_output_path = None
    test_output_path = None
    try:
        # ── TRAIN run: script as-is → score_1 components ──────────────────
        ok, err, train_output_path = _run_variant(script, case_dir, gt_path, "train")
        row["train_run_ok"] = ok
        row["train_error"] = err
        if ok:
            try:
                df_output = pd.read_csv(train_output_path, low_memory=False)
                df_gt = pd.read_csv(gt_path, low_memory=False)
                df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)
                buf = io.StringIO()
                with redirect_stdout(buf), redirect_stderr(buf):
                    _, _, _, fd_f1, true_combined_score, debug = value_based_relative_csv_score(
                        df_output, df_gt
                    )
                row.update({
                    "fd_f1": fd_f1,
                    "avg_col_score_1": debug.get("avg_col_score_1"),
                    "row_count_score": debug.get("row_count_score"),
                    "max_missing_score": debug.get("max_missing_score"),
                    "score_1": debug.get("score_1"),
                    "score_2": debug.get("score_2"),
                    "row_ratio": debug.get("row_ratio"),
                    "true_combined_score": true_combined_score,
                })
            except Exception as e:
                row["train_run_ok"] = True
                row["train_error"] = f"score_failed: {str(e)[:150]}"

        # ── TEST run: training_N.csv -> test_N.csv → validation + partial reward ──
        test_script = swap_training_to_test(script)
        ok, err, test_output_path = _run_variant(test_script, case_dir, gt_path, "test")
        row["test_run_ok"] = ok
        row["test_error"] = err
        if ok:
            try:
                df_test_output = pd.read_csv(test_output_path, low_memory=False)
                df_gt = pd.read_csv(gt_path, low_memory=False)
                df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)
                buf = io.StringIO()
                with redirect_stdout(buf), redirect_stderr(buf):
                    _, is_match, _, _ = compare_tables_matching(df_test_output, df_gt)
                    partial_reward, _ = compare_tables_fuzzy(df_test_output, df_gt)
                row.update({
                    "is_match": bool(is_match),
                    "partial_reward": float(partial_reward),
                })
            except Exception as e:
                row["test_run_ok"] = True
                row["test_error"] = f"score_failed: {str(e)[:150]}"

        return row
    finally:
        for p in (train_output_path, test_output_path):
            if p is not None:
                try:
                    p.unlink(missing_ok=True)
                except Exception:
                    pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases_per_length", type=int, default=None,
                         help="Limit to first N cases per length (for smoke testing)")
    parser.add_argument("--lengths", nargs="*", type=int, default=[1, 4, 9])
    parser.add_argument("--workers", type=int, default=30)
    parser.add_argument("--output", default="score_regression_dataset.csv")
    args = parser.parse_args()

    print("Extracting scripts from logs...", flush=True)
    tasks = collect_tasks(args.lengths, args.cases_per_length)
    print(f"{len(tasks)} unique (case, script) tasks to run across lengths {args.lengths}", flush=True)

    out_path = Path(args.output)
    n_train_ok = 0
    n_test_ok = 0
    n_match = 0
    with out_path.open("w", newline="") as f, \
         ProcessPoolExecutor(max_workers=args.workers) as executor:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()

        futures = {executor.submit(process_script, t): t for t in tasks}
        pbar = tqdm(as_completed(futures), total=len(tasks), unit="script")
        for future in pbar:
            length, case_num, it, kind, script, log_score = futures[future]
            try:
                row = future.result()
            except Exception as e:
                row = {"length": length, "case_num": case_num, "iter": it,
                       "kind": kind, "log_score": log_score,
                       "train_run_ok": False, "train_error": f"worker_exception: {str(e)[:150]}",
                       "test_run_ok": False, "test_error": f"worker_exception: {str(e)[:150]}"}
            writer.writerow(row)
            f.flush()
            if row.get("train_run_ok"):
                n_train_ok += 1
            if row.get("test_run_ok"):
                n_test_ok += 1
            if row.get("is_match"):
                n_match += 1
            pbar.set_postfix(train_ok=n_train_ok, test_ok=n_test_ok, is_match=n_match)

    print(f"\n{len(tasks)} script rows -> {out_path}")
    print(f"  train_run_ok: {n_train_ok}/{len(tasks)}")
    print(f"  test_run_ok:  {n_test_ok}/{len(tasks)}")
    print(f"  is_match (correct on test): {n_match}/{len(tasks)}")


if __name__ == "__main__":
    main()
