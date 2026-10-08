"""
analyze_run9_l1_l4_l9_best_score.py
======================================
BEST_SCORE-only results for run9's full L1/L4/L9 coverage:
  L1 -> test_script_1.sh  (logs_langraph/test_script_1,    101 cases 0-100)
  L4 -> test_script_4.sh  (logs_langraph/test_script_4_l4,  100 cases 0-99)
  L9 -> test_script_4.sh  (logs_langraph/test_script_4_l9,  101 cases 0-100)

BEST_SCORE = the actual script the live MCTS run picked
(state["best_score"]/["best_script"], mined from the log via
parse_log_with_scripts), validated against test data.

Usage: python3 analyze_run9_l1_l4_l9_best_score.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import run_and_check
from eval_run8_training import parse_log_with_scripts

CONFIGS = [
    (1, "logs_langraph/test_script_1", 101),
    (4, "logs_langraph/test_script_4_l4", 100),
    (9, "logs_langraph/test_script_4_l9", 101),
]


def process_case(length, log_dir, case_num):
    files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
    if not files:
        return length, case_num, None
    log_file = Path(files[-1])

    root, iter_scripts, global_best_script, global_best_score, total_iters = \
        parse_log_with_scripts(log_file)
    if root is None or total_iters == 0:
        return length, case_num, None

    ok, note = run_and_check(global_best_script, case_num, length=length) if global_best_script else (False, "no_script")
    return length, case_num, (global_best_score, ok)


def main():
    results = {1: {}, 4: {}, 9: {}}
    tasks = [(length, log_dir, c) for length, log_dir, n in CONFIGS for c in range(n)]

    for batch_start in range(0, len(tasks), 20):
        batch = tasks[batch_start:batch_start + 20]
        print(f"\n--- batch {batch_start}-{batch_start+len(batch)-1} ---", flush=True)
        with ProcessPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(process_case, l, d, c): (l, c) for l, d, c in batch}
            for future in as_completed(futures):
                length, c = futures[future]
                try:
                    length_r, case_num, out = future.result()
                except Exception as e:
                    print(f"L{length} c{c} FAILED: {e}", flush=True)
                    continue
                results[length][case_num] = out
                print(f"L{length} c{case_num} done: {out}", flush=True)

    print(f"\n{'='*70}\nBEST_SCORE results\n{'='*70}")
    for length, log_dir, n in CONFIGS:
        cases = list(range(n))
        n_ok = sum(1 for c in cases if results[length].get(c) is not None and results[length][c][1])
        no_log = sorted(c for c in cases if results[length].get(c) is None)
        wrong = sorted(c for c in cases if results[length].get(c) is not None and not results[length][c][1])
        print(f"\nL{length}: {n_ok}/{n} correct")
        print(f"  no_log/0_iters ({len(no_log)}): {no_log}")
        print(f"  wrong ({len(wrong)}): {wrong}")


if __name__ == "__main__":
    main()
