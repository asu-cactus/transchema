"""
analyze_score_weights_60cases_all_methods.py
===========================
5-method comparison (BEST_SCORE, OLD_total_reward, Q_VALUE, LCB_C=0.5,
HYBRID_C=0.1) for the live det_score_value runs launched by
run_score_weights_60cases.sh -- 20 L1 + 20 L4 + 20 L9 cases (fixed subset,
see L{1,4,9}_CASES there), reward computed live during search using whatever
--score_weights was passed for that tag (weightset1/weightset2), so no
rescoring/relookup is needed here -- the scores already embedded in each
log ARE the scores under that weight vector.

Same reconstruction/selection/validation machinery as
analyze_test_script_4_all_methods.py / analyze_l1_training_all_methods.py
(reused unmodified): parse_log_with_scripts for the tree, greedy_tr_path/
greedy_q_path/greedy_path_lcb for the 3 tree-descent methods, flat_hybrid_pick
for HYBRID_C, and run_and_check (real re-execution against TEST data,
compare_tables_matching) for validation.

Usage: python3 analyze_score_weights_60cases_all_methods.py --tag weightset1
       python3 analyze_score_weights_60cases_all_methods.py --tag weightset2
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import extract_all_scored_scripts, run_and_check
from eval_run8_training import parse_log_with_scripts, greedy_tr_path, get_node_script
from analyze_test_script_4_all_methods import (
    METHOD_NAMES, greedy_q_path, greedy_path_lcb, flat_hybrid_pick,
)

# Must match run_score_weights_60cases.sh's L{1,4,9}_CASES exactly.
L1_CASES = [3, 4, 11, 13, 14, 17, 27, 28, 29, 31, 35, 54, 64, 69, 71, 75, 77, 81, 86, 94]
L4_CASES = [0, 11, 13, 19, 20, 25, 27, 28, 35, 43, 48, 53, 54, 57, 69, 75, 83, 89, 91, 97]
L9_CASES = [5, 10, 12, 15, 24, 33, 37, 44, 45, 46, 48, 58, 68, 70, 73, 77, 79, 80, 90, 93]

CASES_BY_LENGTH = {1: L1_CASES, 4: L4_CASES, 9: L9_CASES}


def process_case(case_num: int, log_dir: str, length: int):
    files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
    if not files:
        return case_num, None
    log_file = Path(files[-1])

    root, iter_scripts, global_best_script, global_best_score, total_iters = \
        parse_log_with_scripts(log_file)
    if root is None or total_iters == 0:
        return case_num, None

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

    return case_num, out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", type=str, required=True, help="weightset1 | weightset2")
    parser.add_argument("--workers", type=int, default=20)
    args = parser.parse_args()

    results_by_length = {}
    for length, cases in CASES_BY_LENGTH.items():
        log_dir = f"logs_langraph/score_weights_60cases_{args.tag}_l{length}"
        print(f"\n--- L{length}: {len(cases)} cases ---", flush=True)
        results = {}
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(process_case, c, log_dir, length): c for c in cases}
            for future in as_completed(futures):
                c = futures[future]
                try:
                    case_num, out = future.result()
                except Exception as e:
                    print(f"L{length} c{c} FAILED: {e}", flush=True)
                    continue
                results[case_num] = out
                print(f"L{length} c{case_num} done: {out}", flush=True)
        results_by_length[length] = results

    print(f"\n{'='*100}\nPER-LENGTH BREAKDOWN (tag={args.tag})\n{'='*100}")
    combined = {name: [0, 0] for name in METHOD_NAMES}
    for length, cases in CASES_BY_LENGTH.items():
        results = results_by_length[length]
        print(f"\nL{length}:")
        for name in METHOD_NAMES:
            n = len([c for c in results if results[c] is not None])
            n_ok = sum(1 for c, out in results.items() if out is not None and out[name][1])
            wrong = sorted(c for c, out in results.items() if out is not None and not out[name][1])
            print(f"  {name:<18}: {n_ok}/{n} correct   wrong={wrong}")
            combined[name][0] += n_ok
            combined[name][1] += n

    print(f"\n{'='*100}\nCOMBINED (tag={args.tag}, {sum(len(c) for c in CASES_BY_LENGTH.values())} cases)\n{'='*100}")
    for name in METHOD_NAMES:
        ok, n = combined[name]
        print(f"  {name:<18}: {ok}/{n} ({100*ok/max(n,1):.1f}%)")


if __name__ == "__main__":
    main()
