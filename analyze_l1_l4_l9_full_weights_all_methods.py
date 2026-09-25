"""
analyze_l1_l4_l9_full_weights_all_methods.py
===========================
5-method comparison (BEST_SCORE, OLD_total_reward, Q_VALUE, LCB_C=0.5,
HYBRID_C=0.1) for the live det_score_value full-pool run
(run_l1_l4_l9_weights_full.sh, tag=weightset1): 100 L1 + 100 L4 + 101 L9
cases. Reward computed live during search with weight-set-1's weights baked
in via --score_weights, so no rescoring/relookup is needed.

Reuses analyze_test_script_4_all_methods.process_case unmodified
(length-agnostic, single log directory per length -- no L1 pilot/batch
split needed here since this run used one unified log dir per length).

Usage: python3 analyze_l1_l4_l9_full_weights_all_methods.py [--tag weightset1]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_test_script_4_all_methods import process_case, METHOD_NAMES

CONFIGS = [(1, 100, 2), (4, 100, 4), (9, 101, 2)]  # (length, n_cases, max_depth -- for reference only)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", type=str, default="weightset1")
    parser.add_argument("--workers", type=int, default=20)
    args = parser.parse_args()

    results_by_length = {}
    for length, n_cases, _ in CONFIGS:
        log_dir = f"logs_langraph/l{length}_weights_full_{args.tag}"
        cases = list(range(n_cases))
        print(f"\n--- L{length}: {n_cases} cases ---", flush=True)
        results = {}
        for batch_start in range(0, len(cases), 20):
            batch = cases[batch_start:batch_start + 20]
            with ProcessPoolExecutor(max_workers=args.workers) as executor:
                futures = {executor.submit(process_case, c, log_dir, length): c for c in batch}
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
    for length, n_cases, _ in CONFIGS:
        results = results_by_length[length]
        print(f"\nL{length}:")
        for name in METHOD_NAMES:
            n = len([c for c in results if results[c] is not None])
            n_ok = sum(1 for c, out in results.items() if out is not None and out[name][1])
            wrong = sorted(c for c, out in results.items() if out is not None and not out[name][1])
            no_log = sorted(c for c in range(n_cases) if results.get(c) is None)
            print(f"  {name:<18}: {n_ok}/{n} correct   wrong={wrong}"
                  + (f"   no_log={no_log}" if no_log and name == METHOD_NAMES[0] else ""))
            combined[name][0] += n_ok
            combined[name][1] += n

    print(f"\n{'='*100}\nCOMBINED (tag={args.tag}, {sum(n for _, n, _ in CONFIGS)} cases)\n{'='*100}")
    for name in METHOD_NAMES:
        ok, n = combined[name]
        print(f"  {name:<18}: {ok}/{n} ({100*ok/max(n,1):.1f}%)")

    print("\n  (compare to trusted equal-weight baseline: L1=84/100, L4=39/86, L9=68/101, HYBRID_C combined=191/287)")


if __name__ == "__main__":
    main()
