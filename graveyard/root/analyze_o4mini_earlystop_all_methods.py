"""
analyze_o4mini_earlystop_all_methods.py
=========================================
For the o4-mini + early_stopping retry of HYBRID_C=0.1-failed cases
(run_o4mini_earlystop_hybrid_failed.sh), reconstruct each case's MCTS tree
and compare 5 final-answer-selection strategies:

  BEST_SCORE, OLD_total_reward, Q_VALUE, LCB_C=0.5, HYBRID_C=0.1

Each method's pick is validated against TEST data (length-parameterized via
validate_output(..., length=L)).

Usage: python3 analyze_o4mini_earlystop_all_methods.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
import math
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import extract_all_scored_scripts, run_and_check
from eval_run8_training import parse_log_with_scripts, greedy_tr_path, get_node_script

METHOD_NAMES = ["BEST_SCORE", "OLD_total_reward", "Q_VALUE", "LCB_C=0.5", "HYBRID_C=0.1"]

L1_CASES = [8, 22, 24, 44, 54, 64, 75, 85, 86, 89, 90, 91, 93, 95, 97, 99]
L4_CASES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
            22, 23, 24, 28, 29, 30, 35, 36, 37, 40, 43, 45, 46, 47, 48, 49, 50, 51, 52,
            53, 58, 60, 61, 62, 63, 64, 68, 70, 71, 73, 84, 86, 87, 92, 93, 94, 96, 97,
            98, 99]
L9_CASES = [1, 3, 4, 13, 15, 16, 19, 20, 21, 22, 23, 24, 27, 29, 35, 36, 38, 40, 41, 42,
            43, 44, 45, 46, 62, 67, 68, 69, 70, 71, 72, 73, 74]

TASKS = [(1, c) for c in L1_CASES] + [(4, c) for c in L4_CASES] + [(9, c) for c in L9_CASES]


def log_dir_for(length: int) -> str:
    return f"logs_langraph/o4mini_earlystop_hybrid_failed_l{length}"


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


def flat_hybrid_pick(entries, C):
    all_scores = [round(e[3], 4) for e in entries]
    freq_map = {}
    for s in all_scores:
        freq_map[s] = freq_map.get(s, 0) + 1
    seen = {}
    for it, kind, script, score in entries:
        key = script.strip()
        if key not in seen or score > seen[key][1]:
            seen[key] = (script, score)
    best_hybrid, best_script, best_score = -999, None, None
    for key, (script, score) in seen.items():
        r = round(score, 4)
        f = freq_map.get(r, 1)
        hybrid = score - C / math.sqrt(f)
        if hybrid > best_hybrid:
            best_hybrid = hybrid
            best_script = script
            best_score = score
    return best_script, best_score


def process_case(length: int, case_num: int):
    log_dir = log_dir_for(length)
    files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
    if not files:
        return length, case_num, None
    log_file = Path(files[-1])

    root, iter_scripts, global_best_script, global_best_score, total_iters = \
        parse_log_with_scripts(log_file)
    if root is None or total_iters == 0:
        return length, case_num, None

    entries = extract_all_scored_scripts(log_file)

    out = {}
    ok, note = run_and_check(global_best_script, case_num, length=length) if global_best_script else (False, "no_script")
    out["BEST_SCORE"] = (global_best_score, ok)

    for name, path_fn in [("OLD_total_reward", greedy_tr_path), ("Q_VALUE", greedy_q_path),
                           ("LCB_C=0.5", lambda rt: greedy_path_lcb(rt, 0.5))]:
        path = path_fn(root)
        leaf = path[-1]
        script = get_node_script(leaf, iter_scripts)
        ok, note = run_and_check(script, case_num, length=length) if script else (False, "no_script")
        out[name] = (leaf.best, ok)

    script, score = flat_hybrid_pick(entries, 0.1) if entries else (None, None)
    ok, note = run_and_check(script, case_num, length=length) if script else (False, "no_script")
    out["HYBRID_C=0.1"] = (score, ok)

    return length, case_num, out


def main():
    results = {1: {}, 4: {}, 9: {}}
    for batch_start in range(0, len(TASKS), 20):
        batch = TASKS[batch_start:batch_start + 20]
        print(f"\n--- batch {batch_start}-{batch_start+len(batch)-1} ---", flush=True)
        with ProcessPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(process_case, length, c): (length, c) for length, c in batch}
            for future in as_completed(futures):
                length, c = futures[future]
                try:
                    length_r, case_num, out = future.result()
                except Exception as e:
                    print(f"L{length} c{c} FAILED: {e}", flush=True)
                    continue
                results[length][case_num] = out
                print(f"L{length} c{case_num} done: {out}", flush=True)

    for length, cases in [(1, L1_CASES), (4, L4_CASES), (9, L9_CASES)]:
        print(f"\n{'='*70}\nL{length}\n{'='*70}")
        for name in METHOD_NAMES:
            n = len(cases)
            n_ok = sum(1 for c in cases if results[length].get(c) is not None and results[length][c][name][1])
            wrong = sorted(c for c in cases if results[length].get(c) is None or not results[length][c][name][1])
            print(f"  {name:<18}: {n_ok}/{n} correct   wrong={wrong}")


if __name__ == "__main__":
    main()
