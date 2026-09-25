"""
analyze_l1_l4_l9_full_bestscore_hybrid.py
===========================
Slimmed version of analyze_l1_l4_l9_full_weights_all_methods.py: only
BEST_SCORE and HYBRID_C=0.1 (skips OLD_total_reward/Q_VALUE/LCB_C=0.5's
tree-descent + real-execution work, which is what made the full 5-method
version too slow on the 301-case full pool).

Usage: python3 analyze_l1_l4_l9_full_bestscore_hybrid.py [--tag weightset1] [--workers 40]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import extract_all_scored_scripts, run_and_check
from eval_run8_training import parse_log_with_scripts
from analyze_test_script_4_all_methods import flat_hybrid_pick

CONFIGS = [(1, list(range(100))), (4, list(range(100))), (9, list(range(101)))]


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
    ok, _ = run_and_check(global_best_script, case_num, length=length) if global_best_script else (False, "no_script")
    out["BEST_SCORE"] = (global_best_score, ok)

    script, score = flat_hybrid_pick(entries, 0.1) if entries else (None, None)
    ok, _ = run_and_check(script, case_num, length=length) if script else (False, "no_script")
    out["HYBRID_C=0.1"] = (score, ok)

    return case_num, out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", type=str, default="weightset1")
    parser.add_argument("--workers", type=int, default=40)
    args = parser.parse_args()

    results_by_length = {}
    for length, cases in CONFIGS:
        log_dir = f"logs_langraph/l{length}_weights_full_{args.tag}"
        print(f"\n--- L{length}: {len(cases)} cases ---", flush=True)
        results = {}
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(process_case, c, log_dir, length): c for c in cases}
            for future in tqdm(as_completed(futures), total=len(futures), desc=f"L{length}", unit="case"):
                c = futures[future]
                try:
                    case_num, out = future.result()
                except Exception as e:
                    tqdm.write(f"L{length} c{c} FAILED: {e}")
                    continue
                results[case_num] = out
                tqdm.write(f"L{length} c{case_num} done: {out}")
        results_by_length[length] = results

    print(f"\n{'='*90}\nPER-LENGTH BREAKDOWN (tag={args.tag})\n{'='*90}")
    combined = {"BEST_SCORE": [0, 0], "HYBRID_C=0.1": [0, 0]}
    for length, cases in CONFIGS:
        results = results_by_length[length]
        print(f"\nL{length}:")
        for name in ["BEST_SCORE", "HYBRID_C=0.1"]:
            n = len([c for c in results if results[c] is not None])
            n_ok = sum(1 for c, out in results.items() if out is not None and out[name][1])
            wrong = sorted(c for c, out in results.items() if out is not None and not out[name][1])
            no_log = sorted(c for c in cases if results.get(c) is None)
            print(f"  {name:<14}: {n_ok}/{n} correct   wrong={wrong}"
                  + (f"   no_log={no_log}" if no_log and name == "BEST_SCORE" else ""))
            combined[name][0] += n_ok
            combined[name][1] += n

    print(f"\n{'='*90}\nCOMBINED (tag={args.tag}, {sum(len(c) for _, c in CONFIGS)} cases)\n{'='*90}")
    for name in ["BEST_SCORE", "HYBRID_C=0.1"]:
        ok, n = combined[name]
        print(f"  {name:<14}: {ok}/{n} ({100*ok/max(n,1):.1f}%)")


if __name__ == "__main__":
    main()
