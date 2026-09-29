"""
analyze_run9_reward_path_vs_maxscore.py
========================================
For each run9 pilot L1 case, reconstruct the MCTS tree from the log (using
the same parser as eval_run8_training.py) and compare two script-selection
strategies:

  OLD (accumulated total_reward): greedy_tr_path(root) leaf's cached script
      -- this is what extract_best() used to do before the max-score change.
  NEW (global best score): global_best_script tracked during parsing
      -- this is what extract_best() does now (state["best_score"]/["best_script"]).

Both are validated against TEST data with compare_tables_matching, so we can
see how many of the 20 pilot cases the OLD selection method would have gotten
right, purely from the trees this run already built (no re-running MCTS).

Usage: python3 analyze_run9_reward_path_vs_maxscore.py
Run from: ~/transchema/  (needs `source env/bin/activate`)
"""
import sys
import glob
from pathlib import Path

sys.path.insert(0, ".")

from eval_run8_training import (
    parse_log_with_scripts, greedy_tr_path, best_on_path, get_node_script,
    swap_training_to_test, run_script, validate_output,
)

LOG_DIR = "logs_langraph/rag_det_score_run9_l1_pilot20"
WORK_DIR = Path(".").resolve()
CASES = list(range(20))


def latest_log(case_num: int) -> Path:
    files = sorted(glob.glob(f"{LOG_DIR}/cases_c{case_num}/*.log"))
    return Path(files[-1]) if files else None


def eval_script(script: str, case_num: int):
    if not script:
        return False, "no_script"
    test_script = swap_training_to_test(script)
    ok, err = run_script(test_script, WORK_DIR)
    if not ok:
        return False, f"run_failed:{err[:60]}"
    correct, sim = validate_output(case_num, WORK_DIR)
    return correct, f"sim={sim:.3f}"


def main():
    rows = []
    for c in CASES:
        log_file = latest_log(c)
        if log_file is None:
            print(f"c{c}: no log found")
            continue

        root, iter_scripts, global_best_script, global_best_score, total_iters = \
            parse_log_with_scripts(log_file)

        if root is None or total_iters == 0:
            print(f"c{c}: parse failed / 0 iters")
            continue

        path = greedy_tr_path(root)
        leaf = path[-1]
        leaf_script = get_node_script(leaf, iter_scripts)

        new_correct, new_note = eval_script(global_best_script, c)
        old_correct, old_note = eval_script(leaf_script, c)

        rows.append((c, old_correct, new_correct, old_note, new_note))
        print(f"c{c:>2}: OLD(reward-path)={'OK' if old_correct else 'WRONG':<6} ({old_note:<12})  "
              f"NEW(max-score)={'OK' if new_correct else 'WRONG':<6} ({new_note})")

    n = len(rows)
    old_ok = sum(1 for r in rows if r[1])
    new_ok = sum(1 for r in rows if r[2])
    print(f"\n{'='*60}")
    print(f"OLD (accumulated total_reward path): {old_ok}/{n} correct")
    print(f"NEW (global best score):             {new_ok}/{n} correct")
    both_ok = sum(1 for r in rows if r[1] and r[2])
    old_only = sum(1 for r in rows if r[1] and not r[2])
    new_only = sum(1 for r in rows if not r[1] and r[2])
    neither = sum(1 for r in rows if not r[1] and not r[2])
    print(f"Both correct: {both_ok}  OLD-only: {old_only}  NEW-only: {new_only}  Neither: {neither}")
    print("OLD-only cases:", [r[0] for r in rows if r[1] and not r[2]])
    print("NEW-only cases:", [r[0] for r in rows if not r[1] and r[2]])


if __name__ == "__main__":
    main()
