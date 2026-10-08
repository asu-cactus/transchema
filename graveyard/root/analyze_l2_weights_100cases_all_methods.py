"""
analyze_l2_weights_100cases_all_methods.py
===========================
5-method comparison (BEST_SCORE, OLD_total_reward, Q_VALUE, LCB_C=0.5,
HYBRID_C=0.1) for the live det_score_value L2 run (run_l2_weights_100cases.sh,
tag=weightset1), all 100 cases (0-99), max_depth=2. Reward computed live
during search with weight-set-1's weights baked in via --score_weights, so
no rescoring/relookup is needed -- the scores already embedded in each log
ARE the scores under that weight vector.

Reuses analyze_test_script_4_all_methods.process_case unmodified (already
length-agnostic, no L1-specific pilot/batch log_dir logic needed since L2
has one single log directory).

Usage: python3 analyze_l2_weights_100cases_all_methods.py [--tag weightset1]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_test_script_4_all_methods import process_case, METHOD_NAMES

LENGTH = 2
N_CASES = 100


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", type=str, default="weightset1")
    parser.add_argument("--workers", type=int, default=20)
    args = parser.parse_args()

    log_dir = f"logs_langraph/l2_weights_100cases_{args.tag}"
    cases = list(range(N_CASES))

    results = {}
    for batch_start in range(0, len(cases), 20):
        batch = cases[batch_start:batch_start + 20]
        print(f"\n--- batch {batch[0]}-{batch[-1]} ---", flush=True)
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(process_case, c, log_dir, LENGTH): c for c in batch}
            for future in as_completed(futures):
                c = futures[future]
                try:
                    case_num, out = future.result()
                except Exception as e:
                    print(f"c{c} FAILED: {e}", flush=True)
                    continue
                results[case_num] = out
                print(f"c{case_num} done: {out}", flush=True)

    print(f"\n{'='*90}\nL2 (tag={args.tag}, {N_CASES} cases)\n{'='*90}")
    for name in METHOD_NAMES:
        n = len([c for c in results if results[c] is not None])
        n_ok = sum(1 for c, out in results.items() if out is not None and out[name][1])
        wrong = sorted(c for c, out in results.items() if out is not None and not out[name][1])
        no_log = sorted(c for c in results if results[c] is None)
        print(f"  {name:<18}: {n_ok}/{n} ({100*n_ok/max(n,1):.1f}%)   wrong={wrong}")
    no_log = sorted(c for c in results if results[c] is None)
    if no_log:
        print(f"\n  no_log/no_iterations: {no_log}")


if __name__ == "__main__":
    main()
