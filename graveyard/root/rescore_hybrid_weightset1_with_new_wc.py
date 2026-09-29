"""
rescore_hybrid_weightset1_with_new_wc.py
===========================
Same idea as rescore_hybrid_weightset1_with_weightset2.py, but rescoring
HYBRID_C's score(i) term with the NEW jointly-fit (w*, C*) from
fit_hybrid_c_and_weights_freq_logreg.py instead of weight-set-2. Reward/
search and freq all stay exactly as weight-set-1's live 60-case run
produced them (fixed, historical) -- only score(i) and C change, recomputed
straight from the per-event `components={...}` already logged, no re-run.

hybrid(i) = (w* . components_i) - C* / sqrt(freq[round(old_score_i, 4)])

Usage: python3 rescore_hybrid_weightset1_with_new_wc.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import run_and_check
from analyze_score_weights_60cases_all_methods import CASES_BY_LENGTH
from rescore_hybrid_weightset1_with_weightset2 import (
    extract_all_scored_scripts_with_components, rescored_hybrid_pick,
)

W_NEW = {
    "fd_f1": 3.7339079369046386,
    "avg_col_score_1": 9.396502151757769,
    "row_count_score": 10.91536824189429,
    "max_missing_score": 8.055871404061822,
}
C_NEW = 5.0728


def process_case(case_num: int, log_dir: str, length: int):
    files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
    if not files:
        return case_num, None
    log_file = Path(files[-1])
    entries = extract_all_scored_scripts_with_components(log_file)
    if not entries:
        return case_num, None

    script, new_score = rescored_hybrid_pick(entries, W_NEW, C_NEW)
    ok, note = run_and_check(script, case_num, length=length) if script else (False, "no_script")
    return case_num, (new_score, ok)


def main():
    print(f"New weights: {W_NEW}")
    print(f"New C: {C_NEW}\n")

    results_by_length = {}
    for length, cases in CASES_BY_LENGTH.items():
        log_dir = f"logs_langraph/score_weights_60cases_weightset1_l{length}"
        print(f"\n--- L{length}: {len(cases)} cases ---", flush=True)
        results = {}
        with ProcessPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(process_case, c, log_dir, length): c for c in cases}
            for future in as_completed(futures):
                c = futures[future]
                try:
                    case_num, out = future.result()
                except Exception as e:
                    print(f"L{length} c{c} FAILED: {e}", flush=True)
                    continue
                results[case_num] = out
                print(f"L{length} c{case_num}: {out}", flush=True)
        results_by_length[length] = results

    print(f"\n{'='*70}\nHYBRID_C rescored with NEW (w*, C*={C_NEW})\n"
          f"(on weight-set-1's live run: same search/tree/freq, only score(i)+C change)\n{'='*70}")
    combined_ok = combined_n = 0
    for length, cases in CASES_BY_LENGTH.items():
        results = results_by_length[length]
        n = len([c for c in results if results[c] is not None])
        n_ok = sum(1 for c, out in results.items() if out is not None and out[1])
        wrong = sorted(c for c, out in results.items() if out is not None and not out[1])
        print(f"  L{length}: {n_ok}/{n} correct   wrong={wrong}")
        combined_ok += n_ok
        combined_n += n
    print(f"\n  COMBINED: {combined_ok}/{combined_n} ({100*combined_ok/max(combined_n,1):.1f}%)")
    print("\n  (compare to weight-set-1's NATIVE HYBRID_C=0.1: 39/60 = 65.0%)")
    print("  (compare to weight-set-1-search + weight-set-2-FAS rescore: 37/60 (61.7%) via fair accounting)")


if __name__ == "__main__":
    main()
