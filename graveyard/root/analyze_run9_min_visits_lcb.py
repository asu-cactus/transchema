"""
analyze_run9_min_visits_lcb.py
================================
Test min-visit-count thresholds and lower-confidence-bound (LCB) variants of
the greedy Q-value path, on the run9 pilot's already-built trees (no
re-running MCTS). Compares against the plain Q-value path (min_visits=0 /
no confidence adjustment) to see which final-answer-selection rule performs
best on the 20 L1 pilot cases.

Usage: python3 analyze_run9_min_visits_lcb.py
Run from: ~/transchema/  (needs `source env/bin/activate`)
"""
import sys
import glob
import math
from pathlib import Path

sys.path.insert(0, ".")

from eval_run8_training import (
    parse_log_with_scripts, get_node_script, swap_training_to_test, run_script, validate_output,
)

LOG_DIR = "logs_langraph/rag_det_score_run9_l1_pilot20"
WORK_DIR = Path(".").resolve()
CASES = list(range(20))


def greedy_path_min_visits(root, min_visits):
    path = [root]
    node = root
    while node.children:
        eligible = [c for c in node.children.values() if c.visits > min_visits]
        pool = eligible if eligible else list(node.children.values())
        node = max(pool, key=lambda c: (c.total_reward / c.visits if c.visits else -1.0, c.visits))
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


def main():
    trees = {}
    for c in CASES:
        files = sorted(glob.glob(f"{LOG_DIR}/cases_c{c}/*.log"))
        if not files:
            continue
        root, iter_scripts, global_best_script, global_best_score, total_iters = \
            parse_log_with_scripts(Path(files[-1]))
        if root is None or total_iters == 0:
            continue
        trees[c] = (root, iter_scripts)
        print(f"parsed c{c}: total_iters={total_iters}", flush=True)

    variants = {
        "plain_q":      lambda root: greedy_path_min_visits(root, 0),
        "min_visits>1": lambda root: greedy_path_min_visits(root, 1),
        "min_visits>2": lambda root: greedy_path_min_visits(root, 2),
        "min_visits>3": lambda root: greedy_path_min_visits(root, 3),
        "LCB_C=0.5":    lambda root: greedy_path_lcb(root, 0.5),
        "LCB_C=1.0":    lambda root: greedy_path_lcb(root, 1.0),
    }

    results = {name: [] for name in variants}
    for c, (root, iter_scripts) in trees.items():
        for name, path_fn in variants.items():
            path = path_fn(root)
            leaf = path[-1]
            script = get_node_script(leaf, iter_scripts)
            correct = eval_script(script, c)
            results[name].append((c, correct))
        print(f"c{c} evaluated across all variants", flush=True)

    print(f"\n{'case':<6}" + "".join(f"{name:<16}" for name in variants))
    for c in trees:
        row = f"{c:<6}"
        for name in variants:
            v = dict(results[name])
            row += f"{'OK' if v.get(c) else 'WRONG':<16}"
        print(row)

    print()
    for name, rows in results.items():
        n_ok = sum(1 for _, ok in rows if ok)
        wrong = [c for c, ok in rows if not ok]
        print(f"{name:<16}: {n_ok}/{len(rows)} correct  wrong={wrong}")


if __name__ == "__main__":
    main()
