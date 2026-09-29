"""
analyze_equal_weight_60cases_all_methods.py
===========================
5-method comparison (BEST_SCORE, OLD_total_reward, Q_VALUE, LCB_C=0.5,
HYBRID_C=0.1) for equal-weight (0.25 each) scoring, restricted to the SAME
fixed 60-case subset used by run_score_weights_60cases.sh (20 L1 + 20 L4 +
20 L9, see CASES_BY_LENGTH in analyze_score_weights_60cases_all_methods.py)
-- for a true apples-to-apples 3-way comparison against weight-set-1 and
weight-set-2's live runs.

No new run needed: these case IDs are a subset of the ORIGINAL equal-weight
baseline pools (rag_det_score_run9_l1_pilot20/batch for L1, test_script_4_l4/
l9 for L4/L9), which already exist. Reuses process_case unmodified from
analyze_l1_training_all_methods.py (L1) and analyze_test_script_4_all_methods.py
(L4/L9) -- the exact same real-execution/validation machinery already used
for the trusted 84/100, 39/86, 68/101 baseline -- just filtered to our 60
case IDs instead of the full 100/100/101.

Usage: python3 analyze_equal_weight_60cases_all_methods.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_l1_training_all_methods import process_case as process_case_l1
from analyze_test_script_4_all_methods import process_case as process_case_l4l9, METHOD_NAMES
from analyze_score_weights_60cases_all_methods import CASES_BY_LENGTH


def main():
    results_by_length = {}

    for length, cases in CASES_BY_LENGTH.items():
        print(f"\n--- L{length}: {len(cases)} cases (equal-weight baseline logs) ---", flush=True)
        results = {}
        with ProcessPoolExecutor(max_workers=20) as executor:
            if length == 1:
                futures = {executor.submit(process_case_l1, c): c for c in cases}
            else:
                log_dir = f"logs_langraph/test_script_4_l{length}"
                futures = {executor.submit(process_case_l4l9, c, log_dir, length): c for c in cases}
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

    print(f"\n{'='*100}\nPER-LENGTH BREAKDOWN (equal-weight, 60-case subset)\n{'='*100}")
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

    print(f"\n{'='*100}\nCOMBINED (equal-weight, {sum(len(c) for c in CASES_BY_LENGTH.values())} cases)\n{'='*100}")
    for name in METHOD_NAMES:
        ok, n = combined[name]
        print(f"  {name:<18}: {ok}/{n} ({100*ok/max(n,1):.1f}%)")


if __name__ == "__main__":
    main()
