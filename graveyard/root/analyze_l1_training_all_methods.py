"""
analyze_l1_training_all_methods.py
=====================================
Real (full script-execution) 5-method comparison for L1 TRAINING split
(rag_det_score_run9_l1_pilot20 [0-19] + rag_det_score_run9_l1_batch_20to100
[20-99], 100 cases, max_depth=2) -- the L1 analog of
analyze_test_script_4_all_methods.py, needed as ground truth for the
lookup+fallback comparison against the new weights.

Usage: python3 analyze_l1_training_all_methods.py
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
from analyze_test_script_4_all_methods import METHOD_NAMES, greedy_q_path, greedy_path_lcb, flat_hybrid_pick

PILOT_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_pilot20"
BATCH_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_batch_20to100"
LENGTH = 1
N_CASES = 100


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

    entries = extract_all_scored_scripts(log_file)

    out = {}
    ok, note = run_and_check(global_best_script, case_num, length=LENGTH) if global_best_script else (False, "no_script")
    out["BEST_SCORE"] = (global_best_score, ok)

    for name, path_fn in [("OLD_total_reward", greedy_tr_path), ("Q_VALUE", greedy_q_path),
                           ("LCB_C=0.5", lambda rt: greedy_path_lcb(rt, 0.5))]:
        path = path_fn(root)
        leaf = path[-1]
        script = get_node_script(leaf, iter_scripts)
        ok, note = run_and_check(script, case_num, length=LENGTH) if script else (False, "no_script")
        out[name] = (leaf.best, ok)

    script, score = flat_hybrid_pick(entries, 0.1) if entries else (None, None)
    ok, note = run_and_check(script, case_num, length=LENGTH) if script else (False, "no_script")
    out["HYBRID_C=0.1"] = (score, ok)

    return case_num, out


def main():
    cases = list(range(N_CASES))
    results = {}
    for batch_start in range(0, len(cases), 20):
        batch = cases[batch_start:batch_start + 20]
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
