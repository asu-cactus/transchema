"""
analyze_o4mini_retry_both_hybrid.py
===========================
Simplified from analyze_o4mini_retry_all_methods_both_hybrid.py: only the
two HYBRID_C variants (native weight-set-1/C=0.1, and rescored with the
jointly-fit w*,C*) for the o4-mini retry of L1+L4+L9's gpt-4.1-mini/
weight-set-1 wrong cases -- no tree reconstruction / other 4 methods, which
is what made the full version too slow.

Also stitches with the original gpt-4.1-mini full-pool results: every case
NOT in the retry set is correct under BOTH variants by construction (that's
what "not in the union of wrong" means) and keeps its gpt-4.1-mini result;
every case IN the retry set is fully replaced by its o4-mini result for that
variant -- so no case is ever counted from two sources.

Usage: python3 analyze_o4mini_retry_both_hybrid.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import run_and_check
from analyze_test_script_4_all_methods import flat_hybrid_pick
from rescore_hybrid_weightset1_with_weightset2 import extract_all_scored_scripts_with_components, rescored_hybrid_pick
from rescore_hybrid_weightset1_with_new_wc import W_NEW, C_NEW

RETRY_TAG = "weightset1_o4mini_retry"

RETRY_CASES = {
    1: [8, 22, 24, 27, 42, 43, 44, 54, 64, 81, 86, 90, 91, 95, 96, 97, 99],
    4: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29,
        32, 36, 37, 45, 46, 47, 48, 49, 50, 51, 52, 53, 55, 60, 61, 62, 64, 67, 68, 70, 73, 78, 86, 87, 92, 93,
        94, 96, 97, 98, 99],
    9: [1, 3, 4, 13, 15, 20, 21, 27, 28, 29, 33, 35, 36, 38, 40, 41, 42, 44, 45, 46, 67, 69, 70, 71, 72, 73, 74],
}
NO_LOG_CASES = {1: [], 4: [12, 30, 33, 63], 9: [43, 62]}
FULL_POOL_SIZE = {1: 100, 4: 100, 9: 101}


def process_case_o4mini(length: int, case_num: int):
    log_dir = f"logs_langraph/l{length}_{RETRY_TAG}"
    files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
    if not files:
        return length, case_num, None
    log_file = Path(files[-1])

    entries = extract_all_scored_scripts_with_components(log_file)
    if not entries:
        return length, case_num, {"native": False, "rescored": False}

    plain_entries = [(it, kind, script, old_score) for it, kind, script, old_score, components in entries]
    native_script, _ = flat_hybrid_pick(plain_entries, 0.1)
    native_ok, _ = run_and_check(native_script, case_num, length=length) if native_script else (False, "no_script")

    new_script, _ = rescored_hybrid_pick(entries, W_NEW, C_NEW)
    if new_script and native_script and new_script.strip() == native_script.strip():
        rescored_ok = native_ok
    else:
        rescored_ok, _ = run_and_check(new_script, case_num, length=length) if new_script else (False, "no_script")

    return length, case_num, {"native": native_ok, "rescored": rescored_ok}


def main():
    o4mini_results = {}
    for length, cases in RETRY_CASES.items():
        print(f"\n--- L{length} o4-mini retry: {len(cases)} cases ---", flush=True)
        results = {}
        with ProcessPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(process_case_o4mini, length, c): c for c in cases}
            for future in as_completed(futures):
                c = futures[future]
                try:
                    _, case_num, out = future.result()
                except Exception as e:
                    print(f"L{length} c{c} FAILED: {e}", flush=True)
                    continue
                results[case_num] = out
                print(f"L{length} c{case_num}: {out}", flush=True)
        o4mini_results[length] = results

    print(f"\n{'='*100}\nO4-MINI RETRY -- both hybrid variants\n{'='*100}")
    for length, cases in RETRY_CASES.items():
        results = o4mini_results[length]
        n = len([c for c in results if results.get(c) is not None])
        missing = sorted(c for c in cases if results.get(c) is None)
        native_ok = sum(1 for c, out in results.items() if out is not None and out.get("native"))
        rescored_ok = sum(1 for c, out in results.items() if out is not None and out.get("rescored"))
        print(f"\nL{length} ({n}/{len(cases)} with scored entries" + (f", missing={missing}" if missing else "") + "):")
        print(f"  native:   {native_ok}/{n} ({100*native_ok/max(n,1):.1f}%)")
        print(f"  rescored: {rescored_ok}/{n} ({100*rescored_ok/max(n,1):.1f}%)")

    # ── Stitch with the original gpt-4.1-mini full-pool results ──────────
    print(f"\n{'='*100}\nSTITCHED (gpt-4.1-mini base + o4-mini replacing retried cases, no duplication)\n{'='*100}")
    stitched_native_total = stitched_rescored_total = pool_total = 0
    for length, n_pool in FULL_POOL_SIZE.items():
        retry_cases = set(RETRY_CASES[length])
        nolog_cases = set(NO_LOG_CASES[length])
        base_correct = n_pool - len(retry_cases) - len(nolog_cases)

        results = o4mini_results[length]
        native_recovered = sum(1 for c in retry_cases if results.get(c) is not None and results[c].get("native"))
        rescored_recovered = sum(1 for c in retry_cases if results.get(c) is not None and results[c].get("rescored"))
        pending = sorted(c for c in retry_cases if results.get(c) is None)

        stitched_native = base_correct + native_recovered
        stitched_rescored = base_correct + rescored_recovered

        print(f"\nL{length}: pool={n_pool}, base(not retried, correct both)={base_correct}, "
              f"no_log(always wrong)={len(nolog_cases)}, retried={len(retry_cases)}"
              + (f", PENDING(not yet run, counted as wrong)={pending}" if pending else ""))
        print(f"  STITCHED NATIVE:   {stitched_native}/{n_pool} ({100*stitched_native/n_pool:.1f}%)  "
              f"[+{native_recovered} recovered of {len(retry_cases)} retried]")
        print(f"  STITCHED RESCORED: {stitched_rescored}/{n_pool} ({100*stitched_rescored/n_pool:.1f}%)  "
              f"[+{rescored_recovered} recovered of {len(retry_cases)} retried]")

        stitched_native_total += stitched_native
        stitched_rescored_total += stitched_rescored
        pool_total += n_pool

    print(f"\n{'='*100}\nCOMBINED STITCHED ({pool_total} cases)\n{'='*100}")
    print(f"  NATIVE:   {stitched_native_total}/{pool_total} ({100*stitched_native_total/pool_total:.1f}%)")
    print(f"  RESCORED: {stitched_rescored_total}/{pool_total} ({100*stitched_rescored_total/pool_total:.1f}%)")


if __name__ == "__main__":
    main()
