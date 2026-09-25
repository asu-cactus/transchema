"""
compare_weights_o4mini.py
============================
Equal-weight vs new-weight (pairwise-LR) comparison for the o4-mini +
early-stopping HYBRID-failed retry experiment
(logs_langraph/o4mini_earlystop_hybrid_failed_l{1,4,9}), using
score_regression_dataset_o4mini.csv as the component lookup, with fallback
to the REAL validated per-case correctness (from the actual
analyze_o4mini_earlystop_all_methods.py run) for any case the lookup can't
resolve.

Usage: python3 compare_weights_o4mini.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_new_weights_all_methods import (
    parse_log_with_new_rewards, flat_hybrid_pick_new, greedy_tr_path,
    greedy_q_path, greedy_path_lcb, load_lookup, METHOD_NAMES,
)
from analyze_run8_failed_case_scripts import extract_all_scored_scripts

EQUAL_W = {"fd_f1": 0.25, "avg_col_score_1": 0.25, "row_count_score": 0.25, "max_missing_score": 0.25}
NEW_W = {"fd_f1": 0.1241, "avg_col_score_1": 0.2487, "row_count_score": 0.3562, "max_missing_score": 0.2710}

L1_CASES = [8, 22, 24, 44, 54, 64, 75, 85, 86, 89, 90, 91, 93, 95, 97, 99]
L4_CASES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
            22, 23, 24, 28, 29, 30, 35, 36, 37, 40, 43, 45, 46, 47, 48, 49, 50, 51, 52,
            53, 58, 60, 61, 62, 63, 64, 68, 70, 71, 73, 84, 86, 87, 92, 93, 94, 96, 97,
            98, 99]
L9_CASES = [1, 3, 4, 13, 15, 16, 19, 20, 21, 22, 23, 24, 27, 29, 35, 36, 38, 40, 41, 42,
            43, 44, 45, 46, 62, 67, 68, 69, 70, 71, 72, 73, 74]

CONFIGS = [
    (1, "logs_langraph/o4mini_earlystop_hybrid_failed_l1", L1_CASES),
    (4, "logs_langraph/o4mini_earlystop_hybrid_failed_l4", L4_CASES),
    (9, "logs_langraph/o4mini_earlystop_hybrid_failed_l9", L9_CASES),
]

# Real, validated ground truth from analyze_o4mini_earlystop_all_methods.py's
# actual run (confirmed in conversation) -- wrong= lists per method.
GROUND_TRUTH_WRONG = {
    1: {
        "BEST_SCORE": [44, 64, 75, 89, 90, 95, 97, 99],
        "OLD_total_reward": [22, 24, 44, 54, 64, 75, 89, 90, 91, 93, 99],
        "Q_VALUE": [22, 44, 54, 64, 89, 90, 93, 97, 99],
        "LCB_C=0.5": [22, 24, 44, 54, 64, 89, 90, 91, 93, 99],
        "HYBRID_C=0.1": [22, 44, 89, 90, 95, 97, 99],
    },
    4: {
        "BEST_SCORE": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 35, 40, 45, 46, 47, 48, 49, 50, 52, 53, 62, 63, 64, 70, 71, 73, 84, 86, 92, 93, 98],
        "OLD_total_reward": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 35, 40, 45, 46, 47, 48, 49, 50, 51, 52, 53, 60, 61, 62, 63, 64, 68, 70, 71, 73, 86, 87, 92, 93, 98],
        "Q_VALUE": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 35, 40, 45, 46, 47, 48, 49, 50, 51, 52, 53, 60, 62, 63, 64, 70, 71, 73, 86, 87, 92, 93, 98],
        "LCB_C=0.5": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 35, 40, 45, 46, 47, 48, 49, 50, 51, 52, 53, 60, 62, 63, 64, 68, 70, 71, 73, 86, 87, 92, 93, 98],
        "HYBRID_C=0.1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 35, 40, 45, 46, 47, 48, 49, 50, 52, 53, 62, 63, 64, 68, 70, 71, 73, 84, 86, 92, 93, 98],
    },
    9: {
        "BEST_SCORE": [3, 4, 13, 15, 19, 20, 21, 22, 23, 24, 29, 35, 36, 41, 42, 43, 44, 45, 46, 62, 67, 68, 70, 71, 72, 73, 74],
        "OLD_total_reward": [3, 4, 13, 15, 19, 20, 21, 23, 24, 27, 29, 35, 36, 41, 42, 43, 44, 45, 46, 62, 67, 70, 71, 72, 73, 74],
        "Q_VALUE": [3, 4, 13, 15, 19, 20, 21, 23, 24, 27, 29, 35, 36, 41, 42, 43, 44, 45, 46, 62, 67, 70, 71, 72, 73, 74],
        "LCB_C=0.5": [3, 4, 13, 15, 19, 20, 21, 23, 24, 27, 29, 35, 36, 41, 42, 43, 44, 45, 46, 62, 67, 70, 71, 72, 73, 74],
        "HYBRID_C=0.1": [3, 4, 13, 15, 19, 20, 21, 22, 23, 24, 29, 35, 36, 41, 42, 43, 44, 45, 46, 62, 67, 70, 71, 72, 73, 74],
    },
}


def ground_truth_for(length, case_num, method):
    wrong = GROUND_TRUTH_WRONG[length][method]
    return case_num not in wrong


def process_case(length, log_dir, case_num, lookup):
    files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
    if not files:
        return length, case_num, None
    log_file = Path(files[-1])
    lookup_case = lookup.get((str(length), str(case_num)))

    (root, iter_scripts, global_best_script, global_best_score, global_best_is_match,
     total_iters, node_meta, n_miss, n_tot) = parse_log_with_new_rewards(log_file, lookup_case)
    if root is None or total_iters == 0:
        return length, case_num, None

    out = {}
    out["BEST_SCORE"] = (global_best_score, global_best_is_match)

    for name, path_fn in [("OLD_total_reward", greedy_tr_path), ("Q_VALUE", greedy_q_path),
                           ("LCB_C=0.5", lambda rt: greedy_path_lcb(rt, 0.5))]:
        path = path_fn(root)
        leaf = path[-1]
        is_match = node_meta.get(id(leaf))
        out[name] = (leaf.best, is_match)

    entries = extract_all_scored_scripts(log_file)
    hyb_score, hyb_match = flat_hybrid_pick_new(entries, lookup_case, 0.1) if entries else (None, None)
    out["HYBRID_C=0.1"] = (hyb_score, hyb_match)

    return length, case_num, out


def run_all(weights):
    lookup = load_lookup(path="score_regression_dataset_o4mini.csv", weights=weights)
    tasks = [(length, log_dir, c) for length, log_dir, cases in CONFIGS for c in cases]
    results = {1: {}, 4: {}, 9: {}}
    with ProcessPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_case, l, d, c, lookup): (l, c) for l, d, c in tasks}
        for future in as_completed(futures):
            length, c = futures[future]
            try:
                length_r, case_num, out = future.result()
            except Exception as e:
                print(f"L{length} c{c} FAILED: {e}", flush=True)
                continue
            results[length][case_num] = out
    return results


def summarize_with_fallback(results, length, cases):
    row = {}
    for name in METHOD_NAMES:
        n_ok = n_known = 0
        for c in cases:
            out = results[length].get(c)
            is_match = None
            if out is not None:
                score, is_match = out[name]
            if is_match is None:
                is_match = ground_truth_for(length, c, name)  # fallback: real result
            n_known += 1
            n_ok += bool(is_match)
        row[name] = (n_ok, n_known)
    return row


def main():
    print("Running EQUAL-weight lookup pass...", flush=True)
    eq_results = run_all(EQUAL_W)
    print("Running NEW-weight lookup pass...", flush=True)
    new_results = run_all(NEW_W)

    for length, log_dir, cases in CONFIGS:
        eq_row = summarize_with_fallback(eq_results, length, cases)
        new_row = summarize_with_fallback(new_results, length, cases)
        print(f"\n{'='*80}\nL{length} (o4-mini experiment, {len(cases)} cases) -- lookup + real-fallback\n{'='*80}")
        print(f"{'Method':<18}{'Equal-weight':<20}{'New-weight':<20}{'Delta':<10}")
        for name in METHOD_NAMES:
            eo, ek = eq_row[name]
            no, nk = new_row[name]
            print(f"{name:<18}{f'{eo}/{ek}':<20}{f'{no}/{nk}':<20}{no-eo:+d}")


if __name__ == "__main__":
    main()
