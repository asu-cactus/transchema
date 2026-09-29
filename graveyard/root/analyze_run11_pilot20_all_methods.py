"""
analyze_run11_pilot20_all_methods.py
======================================
For the run11 L1 pilot (cases 0-19), reconstruct each case's MCTS tree from
its log and compare 5 final-answer-selection strategies:

  BEST_SCORE   : global max score anywhere in the search
  OLD_total_reward : greedy_tr_path(root) leaf (accumulated total_reward)
  Q_VALUE      : greedy descent by q_value = total_reward/visits
  LCB_C=0.5    : greedy descent by q_value - 0.5/sqrt(visits)
  HYBRID_C=0.1 : flat (no tree-walk) argmax over every distinct script in
                 the log, ranked by score - 0.1/sqrt(freq)

Each method's pick is validated against TEST data.

Runs cases in parallel (ProcessPoolExecutor, 20 workers by default).

Usage: python3 analyze_run11_pilot20_all_methods.py [--workers N]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
import math
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import extract_all_scored_scripts, run_and_check
from eval_run8_training import parse_log_with_scripts, greedy_tr_path, get_node_script

LOG_DIR = "logs_langraph/rag_det_score_run11_l1_pilot20"
CASES = list(range(20))

METHOD_NAMES = ["BEST_SCORE", "OLD_total_reward", "Q_VALUE", "LCB_C=0.5", "HYBRID_C=0.1"]


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


def process_case(case_num: int):
    files = sorted(glob.glob(f"{LOG_DIR}/cases_c{case_num}/*.log"))
    if not files:
        return case_num, None
    log_file = Path(files[-1])

    root, iter_scripts, global_best_script, global_best_score, total_iters = \
        parse_log_with_scripts(log_file)
    if root is None or total_iters == 0:
        return case_num, None

    entries = extract_all_scored_scripts(log_file)

    out = {}

    ok, note = run_and_check(global_best_script, case_num) if global_best_script else (False, "no_script")
    out["BEST_SCORE"] = (global_best_score, ok)

    for name, path_fn in [("OLD_total_reward", greedy_tr_path), ("Q_VALUE", greedy_q_path),
                           ("LCB_C=0.5", lambda rt: greedy_path_lcb(rt, 0.5))]:
        path = path_fn(root)
        leaf = path[-1]
        script = get_node_script(leaf, iter_scripts)
        ok, note = run_and_check(script, case_num) if script else (False, "no_script")
        out[name] = (leaf.best, ok)

    script, score = flat_hybrid_pick(entries, 0.1) if entries else (None, None)
    ok, note = run_and_check(script, case_num) if script else (False, "no_script")
    out["HYBRID_C=0.1"] = (score, ok)

    return case_num, out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=20)
    args = parser.parse_args()

    results = {}
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_case, c): c for c in CASES}
        for future in as_completed(futures):
            c = futures[future]
            try:
                case_num, out = future.result()
            except Exception as e:
                print(f"c{c} FAILED: {e}", flush=True)
                continue
            results[case_num] = out
            print(f"c{case_num} done: {out}", flush=True)

    print(f"\n{'case':<6}" + "".join(f"{name:<18}" for name in METHOD_NAMES))
    for c in sorted(results):
        out = results[c]
        if out is None:
            print(f"{c:<6}NO LOG")
            continue
        row = f"{c:<6}"
        for name in METHOD_NAMES:
            score, ok = out[name]
            score_s = f"{score:.4f}" if score is not None else "N/A"
            tag = "OK" if ok else "WRONG"
            row += f"{score_s}/{tag:<12}"
        print(row)

    print()
    for name in METHOD_NAMES:
        n = len([c for c in results if results[c] is not None])
        n_ok = sum(1 for c, out in results.items() if out is not None and out[name][1])
        wrong = sorted(c for c, out in results.items() if out is not None and not out[name][1])
        print(f"{name:<18}: {n_ok}/{n} correct   wrong={wrong}")


if __name__ == "__main__":
    main()
