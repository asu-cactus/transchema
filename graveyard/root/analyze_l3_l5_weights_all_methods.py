"""
analyze_l3_l5_weights_all_methods.py
===========================
5-method comparison (BEST_SCORE, OLD_total_reward, Q_VALUE, LCB_C=0.5,
HYBRID_C=0.1) for the live det_score_value L3+L5 run
(run_l3_l5_weights.sh, tag=weightset1): L3 100 cases (0-29,31-100, case 30
doesn't exist), L5 98 cases (0-97). Reward computed live during search with
weight-set-1's weights baked in via --score_weights, so no rescoring/
relookup is needed.

Reuses analyze_test_script_4_all_methods.process_case unmodified
(length-agnostic, single log directory per length).

Usage: python3 analyze_l3_l5_weights_all_methods.py [--tag weightset1]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_test_script_4_all_methods import process_case, METHOD_NAMES

CONFIGS = [(3, [c for c in range(101) if c != 30]), (5, list(range(98)))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", type=str, default="weightset1")
    parser.add_argument("--workers", type=int, default=20)
    args = parser.parse_args()

    results_by_length = {}
    for length, cases in CONFIGS:
        log_dir = f"logs_langraph/l{length}_weights_{args.tag}"
        print(f"\n--- L{length}: {len(cases)} cases ---", flush=True)
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
    for length, cases in CONFIGS:
        results = results_by_length[length]
        print(f"\nL{length}:")
        for name in METHOD_NAMES:
            n = len([c for c in results if results[c] is not None])
            n_ok = sum(1 for c, out in results.items() if out is not None and out[name][1])
            wrong = sorted(c for c, out in results.items() if out is not None and not out[name][1])
            no_log = sorted(c for c in cases if results.get(c) is None)
            print(f"  {name:<18}: {n_ok}/{n} correct   wrong={wrong}"
                  + (f"   no_log={no_log}" if no_log and name == METHOD_NAMES[0] else ""))
            combined[name][0] += n_ok
            combined[name][1] += n

    print(f"\n{'='*100}\nCOMBINED L3+L5 (tag={args.tag}, {sum(len(c) for _, c in CONFIGS)} cases)\n{'='*100}")
    for name in METHOD_NAMES:
        ok, n = combined[name]
        print(f"  {name:<18}: {ok}/{n} ({100*ok/max(n,1):.1f}%)")


if __name__ == "__main__":
    main()
