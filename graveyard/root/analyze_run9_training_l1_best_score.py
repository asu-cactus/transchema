"""
analyze_run9_training_l1_best_score.py
=========================================
BEST_SCORE-only results for run9's L1 leg on the TRAINING split
(rag_det_score_run9_l1_pilot20 [cases 0-19] + rag_det_score_run9_l1_batch_20to100
[cases 20-99], both --data_split training, max_depth=2, 100 cases total).

Replaces test_script_1.sh in the L1/L4/L9 comparison, since that script ran
on --data_split test, not training.

Usage: python3 analyze_run9_training_l1_best_score.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import run_and_check
from eval_run8_training import parse_log_with_scripts

PILOT_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_pilot20"
BATCH_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_batch_20to100"
LENGTH = 1
CASES = list(range(100))


def log_dir_for(case_num: int) -> str:
    return PILOT_LOG_DIR if case_num < 20 else BATCH_LOG_DIR


def process_case(case_num: int):
    log_dir = log_dir_for(case_num)
    files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
    if not files:
        return case_num, None
    log_file = Path(files[-1])

    root, iter_scripts, global_best_script, global_best_score, total_iters = \
        parse_log_with_scripts(log_file)
    if root is None or total_iters == 0:
        return case_num, None

    ok, note = run_and_check(global_best_script, case_num, length=LENGTH) if global_best_script else (False, "no_script")
    return case_num, (global_best_score, ok)


def main():
    results = {}
    for batch_start in range(0, len(CASES), 20):
        batch = CASES[batch_start:batch_start + 20]
        print(f"\n--- batch {batch[0]}-{batch[-1]} ---", flush=True)
        with ProcessPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(process_case, c): c for c in batch}
            for future in as_completed(futures):
                c = futures[future]
                try:
                    case_num, out = future.result()
                except Exception as e:
                    print(f"c{c} FAILED: {e}", flush=True)
                    continue
                results[case_num] = out
                print(f"c{case_num} done: {out}", flush=True)

    n_ok = sum(1 for c in CASES if results.get(c) is not None and results[c][1])
    no_log = sorted(c for c in CASES if results.get(c) is None)
    wrong = sorted(c for c in CASES if results.get(c) is not None and not results[c][1])
    print(f"\n{'='*70}\nL1 (training split) BEST_SCORE results\n{'='*70}")
    print(f"L1: {n_ok}/{len(CASES)} correct")
    print(f"  no_log/0_iters ({len(no_log)}): {no_log}")
    print(f"  wrong ({len(wrong)}): {wrong}")


if __name__ == "__main__":
    main()
