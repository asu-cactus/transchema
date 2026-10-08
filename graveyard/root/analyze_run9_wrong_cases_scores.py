"""
analyze_run9_wrong_cases_scores.py
====================================
For a given list of case numbers (the union of cases wrong under any of the
4 selection strategies: BEST_SCORE/live, OLD_total_reward, Q_VALUE,
LCB_C=0.5), report each method's chosen script's score + correctness, plus:

  - BEST_CORRECT score: the highest-scoring script anywhere in the log that
    actually validates correct on TEST data (None if no correct script
    exists anywhere in the log for that case).

Runs cases in parallel (ProcessPoolExecutor, 20 workers by default).

Usage: python3 analyze_run9_wrong_cases_scores.py [--workers N]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
import math
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import extract_all_scored_scripts, run_and_check
from eval_run8_training import parse_log_with_scripts, greedy_tr_path, get_node_script

PILOT_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_pilot20"
BATCH_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_batch_20to100"
PILOT_RESULT_DIR = "Langraph/results_langraph/rag_det_score_run9_l1_pilot20"
BATCH_RESULT_DIR = "Langraph/results_langraph/rag_det_score_run9_l1_batch_20to100"

WRONG_CASES = [3, 4, 6, 8, 9, 10, 16, 18, 22, 24, 35, 37, 41, 43, 44, 53, 54, 56,
               64, 65, 67, 71, 72, 75, 81, 85, 86, 88, 89, 90, 93, 94, 95, 96, 97, 99]


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


def log_dir_for(case_num: int) -> str:
    return PILOT_LOG_DIR if case_num < 20 else BATCH_LOG_DIR


def result_dir_for(case_num: int) -> str:
    return PILOT_RESULT_DIR if case_num < 20 else BATCH_RESULT_DIR


def chosen_score_for(case_num: int):
    """Pull the actual live-run chosen (global best) score from results_summary.csv."""
    prefix = "rag_det_score_run9_l1_pilot20" if case_num < 20 else "rag_det_score_run9_l1_batch"
    result_dir = result_dir_for(case_num)
    dirs = sorted(glob.glob(f"{result_dir}/{prefix}_c{case_num}_*"))
    if not dirs:
        return None
    latest = dirs[-1]
    f = Path(latest) / "results_summary.csv"
    if not f.exists():
        return None
    df = pd.read_csv(f)
    if len(df) == 0:
        return None
    return float(df.iloc[0]["best_score"])


def process_case(case_num: int):
    log_dir = log_dir_for(case_num)
    files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
    if not files:
        return case_num, None

    entries = extract_all_scored_scripts(Path(files[-1]))
    chosen_score = chosen_score_for(case_num)

    if not entries:
        return case_num, {"chosen_score": chosen_score, "best_correct_score": None, "n_correct": 0, "n_total": 0}

    seen = {}
    for it, kind, script, score in entries:
        key = script.strip()
        if key not in seen or score > seen[key][2]:
            seen[key] = (it, kind, score)

    best_correct_score = None
    n_correct = 0
    for script, (it, kind, score) in seen.items():
        correct, note = run_and_check(script, case_num)
        if correct:
            n_correct += 1
            if best_correct_score is None or score > best_correct_score:
                best_correct_score = score

    return case_num, {
        "chosen_score": chosen_score,
        "best_correct_score": best_correct_score,
        "n_correct": n_correct,
        "n_total": len(seen),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=20)
    args = parser.parse_args()

    results = {}
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_case, c): c for c in WRONG_CASES}
        for future in as_completed(futures):
            c = futures[future]
            try:
                case_num, info = future.result()
            except Exception as e:
                print(f"c{c} FAILED: {e}", flush=True)
                continue
            results[case_num] = info
            print(f"c{case_num} done: {info}", flush=True)

    print(f"\n{'case':<6}{'chosen_score':<14}{'best_correct_score':<20}{'n_correct/n_total':<20}")
    for c in sorted(results):
        info = results[c]
        if info is None:
            print(f"{c:<6}NO LOG FOUND")
            continue
        cs = f"{info['chosen_score']:.4f}" if info['chosen_score'] is not None else "N/A"
        bcs = f"{info['best_correct_score']:.4f}" if info['best_correct_score'] is not None else "NONE"
        print(f"{c:<6}{cs:<14}{bcs:<20}{info['n_correct']}/{info['n_total']:<20}")


if __name__ == "__main__":
    main()
