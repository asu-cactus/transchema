"""
analyze_run9_full100_path_comparison.py
=========================================
For all 100 run9 L1 cases (pilot 0-19 + batch 20-99), reconstruct the MCTS
tree from the log and compare 3 final-answer-selection strategies:

  OLD          : greedy_tr_path(root) leaf (accumulated total_reward)
  Q_VALUE      : greedy descent by q_value = total_reward/visits
  LCB_C=0.5    : greedy descent by q_value - 0.5/sqrt(visits)

against the actual live result (global best score, already known: 78/100),
by validating each variant's leaf script against TEST data.

Runs cases in parallel (ProcessPoolExecutor, 20 workers by default).

Usage: python3 analyze_run9_full100_path_comparison.py [--workers N]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
import math
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from eval_run8_training import (
    parse_log_with_scripts, greedy_tr_path, get_node_script,
    swap_training_to_test, run_script, validate_output,
)

PILOT_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_pilot20"
BATCH_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_batch_20to100"
WORK_DIR = Path(".").resolve()
CASES = list(range(100))

VARIANT_NAMES = ["OLD_total_reward", "Q_VALUE", "LCB_C=0.5"]


def log_dir_for(case_num: int) -> str:
    return PILOT_LOG_DIR if case_num < 20 else BATCH_LOG_DIR


def greedy_q_path(root):
    path = [root]
    node = root
    while node.children:
        node = max(node.children.values(),
                    key=lambda c: (c.total_reward / c.visits if c.visits else -1.0, c.visits))
        path.append(node)
    return path


def greedy_path_lcb(root, C):
    path = [root]
    node = root
    while node.children:
        def score(c):
            if c.visits == 0:
                return -1.0
            q = c.total_reward / c.visits
            return q - C / math.sqrt(c.visits)
        node = max(node.children.values(), key=score)
        path.append(node)
    return path


def eval_script(script, case_num):
    if not script:
        return False
    test_script = swap_training_to_test(script)
    ok, err = run_script(test_script, WORK_DIR)
    if not ok:
        return False
    correct, sim = validate_output(case_num, WORK_DIR)
    return correct


def process_case(case_num: int):
    """Runs in a worker process. Returns (case_num, {variant_name: correct_bool} or None)."""
    log_dir = log_dir_for(case_num)
    files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
    if not files:
        return case_num, None

    root, iter_scripts, global_best_script, global_best_score, total_iters = \
        parse_log_with_scripts(Path(files[-1]))
    if root is None or total_iters == 0:
        return case_num, None

    variants = {
        "OLD_total_reward": greedy_tr_path(root),
        "Q_VALUE":           greedy_q_path(root),
        "LCB_C=0.5":         greedy_path_lcb(root, 0.5),
    }

    out = {}
    for name, path in variants.items():
        leaf = path[-1]
        script = get_node_script(leaf, iter_scripts)
        out[name] = eval_script(script, case_num)

    return case_num, out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=20)
    args = parser.parse_args()

    results = {name: {} for name in VARIANT_NAMES}
    skipped = []

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_case, c): c for c in CASES}
        for future in as_completed(futures):
            c = futures[future]
            try:
                case_num, out = future.result()
            except Exception as e:
                print(f"c{c} FAILED: {e}", flush=True)
                skipped.append(c)
                continue
            if out is None:
                skipped.append(case_num)
                print(f"c{case_num} skipped (no log/0 iters)", flush=True)
                continue
            for name in VARIANT_NAMES:
                results[name][case_num] = out[name]
            print(f"c{case_num} done: {out}", flush=True)

    print(f"\nskipped (no log/0 iters): {sorted(skipped)}")
    print()
    for name in VARIANT_NAMES:
        rows = results[name]
        n_ok = sum(1 for ok in rows.values() if ok)
        wrong = sorted(c for c, ok in rows.items() if not ok)
        print(f"{name:<18}: {n_ok}/{len(rows)} correct")
        print(f"  wrong: {wrong}")


if __name__ == "__main__":
    main()
