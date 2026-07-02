"""
analyze_run9_unique_score_analysis.py
=======================================
For each of the 36 "ever wrong" run9 cases, and for each of the 4
selection strategies (BEST_SCORE/live, OLD_total_reward, Q_VALUE,
LCB_C=0.5), report:

  - chosen_score : the score of the script that method picked
  - rank         : where that score ranks among ALL individual scored
                   iterations in the log (1 = highest score seen anywhere)
  - freq         : how many separate iterations in the log produced that
                   exact score (rounded to 4dp)
  - leaf_visits  : the tree node's own visit count for that method's chosen
                   leaf (OLD/Q/LCB only -- BEST_SCORE has no single node)

No script execution / test-data validation here -- correctness per method
is already known from the earlier "right_in" table. This is pure log/tree
parsing (fast), to test whether BEST_SCORE/Q_VALUE win on rare, low-support
"longshot" scores while OLD_total_reward/LCB win on well-supported ones.

Usage: python3 analyze_run9_unique_score_analysis.py [--workers N]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
import math
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import extract_all_scored_scripts
from eval_run8_training import parse_log_with_scripts, greedy_tr_path

PILOT_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_pilot20"
BATCH_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_batch_20to100"

WRONG_CASES = [3, 4, 6, 8, 9, 10, 16, 18, 22, 24, 35, 37, 41, 43, 44, 53, 54, 56,
               64, 65, 67, 71, 72, 75, 81, 85, 86, 88, 89, 90, 93, 94, 95, 96, 97, 99]


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


def rank_and_freq(score, sorted_unique_desc, freq_map):
    if score is None:
        return None, 0
    r = round(score, 4)
    try:
        rank = sorted_unique_desc.index(r) + 1
    except ValueError:
        rank = None
    freq = freq_map.get(r, 0)
    return rank, freq


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

    entries = extract_all_scored_scripts(log_file)  # (iter, kind, script, score)
    all_scores = [round(e[3], 4) for e in entries]
    freq_map = {}
    for s in all_scores:
        freq_map[s] = freq_map.get(s, 0) + 1
    sorted_unique_desc = sorted(freq_map.keys(), reverse=True)

    methods = {}

    r, f = rank_and_freq(global_best_score, sorted_unique_desc, freq_map)
    methods["BEST"] = {"score": global_best_score, "rank": r, "freq": f, "leaf_visits": None}

    for name, path_fn in [("OLD", greedy_tr_path), ("Q", greedy_q_path),
                           ("LCB", lambda rt: greedy_path_lcb(rt, 0.5))]:
        path = path_fn(root)
        leaf = path[-1]
        r, f = rank_and_freq(leaf.best, sorted_unique_desc, freq_map)
        methods[name] = {"score": leaf.best, "rank": r, "freq": f, "leaf_visits": leaf.visits}

    return case_num, {"methods": methods, "n_unique_scores": len(sorted_unique_desc),
                       "n_total_iters": len(all_scores)}


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
            print(f"c{case_num} done", flush=True)

    print(f"\n{'case':<6}{'method':<7}{'score':<10}{'rank':<8}{'freq':<7}{'leaf_visits':<13}{'n_unique/n_total'}")
    for c in sorted(results):
        info = results[c]
        if info is None:
            print(f"{c:<6}NO LOG")
            continue
        for m in ["BEST", "OLD", "Q", "LCB"]:
            d = info["methods"][m]
            score_s = f"{d['score']:.4f}" if d["score"] is not None else "N/A"
            rank_s = str(d["rank"]) if d["rank"] is not None else "?"
            lv_s = str(d["leaf_visits"]) if d["leaf_visits"] is not None else "-"
            print(f"{c:<6}{m:<7}{score_s:<10}{rank_s:<8}{d['freq']:<7}{lv_s:<13}"
                  f"{info['n_unique_scores']}/{info['n_total_iters']}")


if __name__ == "__main__":
    main()
