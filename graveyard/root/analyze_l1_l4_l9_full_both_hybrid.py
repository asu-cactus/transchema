"""
analyze_l1_l4_l9_full_both_hybrid.py
===========================
For the L1+L4+L9 full-pool live run (run_l1_l4_l9_weights_full.sh,
tag=weightset1: 100 L1 + 100 L4 + 101 L9 cases), report HYBRID_C=0.1 two
ways, same pattern as rescore_hybrid_l2_weightset1_with_new_wc.py:

  (A) NATIVE   -- the score already embedded in each log (weight-set-1's
                  own weights, C=0.1 fixed) -- what
                  analyze_l1_l4_l9_full_weights_all_methods.py already
                  reports for HYBRID_C=0.1.
  (B) RESCORED -- score(i) recomputed from each event's logged raw
                  components under the jointly-fit (w*, C*) from
                  fit_hybrid_c_and_weights_freq_logreg.py (unnormalized
                  weights + the fitted C=5.0728 -- "weighted C"). freq
                  stays exactly as weight-set-1's live search produced it
                  (fixed, historical) -- nothing is re-run, purely log
                  parsing + real re-execution of whichever script each
                  variant picks.

Usage: python3 analyze_l1_l4_l9_full_both_hybrid.py
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

TAG = "weightset1"
CONFIGS = [(1, 100), (4, 100), (9, 101)]  # (length, n_cases)


def process_case(length: int, case_num: int):
    log_dir = f"logs_langraph/l{length}_weights_full_{TAG}"
    files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
    if not files:
        return length, case_num, None
    log_file = Path(files[-1])
    entries = extract_all_scored_scripts_with_components(log_file)
    if not entries:
        return length, case_num, None

    plain_entries = [(it, kind, script, old_score) for it, kind, script, old_score, components in entries]
    native_script, native_score = flat_hybrid_pick(plain_entries, 0.1)
    native_ok, _ = run_and_check(native_script, case_num, length=length) if native_script else (False, "no_script")

    new_script, new_score = rescored_hybrid_pick(entries, W_NEW, C_NEW)
    if new_script and new_script.strip() == (native_script or "").strip():
        new_ok = native_ok  # same script picked -- reuse the execution result
    else:
        new_ok, _ = run_and_check(new_script, case_num, length=length) if new_script else (False, "no_script")

    return length, case_num, {
        "native": (native_score, native_ok),
        "rescored": (new_score, new_ok),
    }


def main():
    print(f"New (w*, C*): {W_NEW}, C={C_NEW}\n")

    results_by_length = {}
    for length, n_cases in CONFIGS:
        cases = list(range(n_cases))
        print(f"\n--- L{length}: {n_cases} cases ---", flush=True)
        results = {}
        for batch_start in range(0, len(cases), 20):
            batch = cases[batch_start:batch_start + 20]
            with ProcessPoolExecutor(max_workers=20) as executor:
                futures = {executor.submit(process_case, length, c): c for c in batch}
                for future in as_completed(futures):
                    c = futures[future]
                    try:
                        _, case_num, out = future.result()
                    except Exception as e:
                        print(f"L{length} c{c} FAILED: {e}", flush=True)
                        continue
                    results[case_num] = out
                    print(f"L{length} c{case_num}: {out}", flush=True)
        results_by_length[length] = results

    print(f"\n{'='*100}\nHYBRID_C=0.1 -- NATIVE vs RESCORED (new w*,C*), L1+L4+L9 full pool\n{'='*100}")
    combined_native_ok = combined_rescored_ok = combined_n = 0
    for length, n_cases in CONFIGS:
        results = results_by_length[length]
        n = len([c for c in results if results[c] is not None])
        native_ok = sum(1 for c, out in results.items() if out is not None and out["native"][1])
        rescored_ok = sum(1 for c, out in results.items() if out is not None and out["rescored"][1])
        native_wrong = sorted(c for c, out in results.items() if out is not None and not out["native"][1])
        rescored_wrong = sorted(c for c, out in results.items() if out is not None and not out["rescored"][1])
        no_log = sorted(c for c in range(n_cases) if results.get(c) is None)
        print(f"\nL{length} ({n}/{n_cases} with scored entries):")
        print(f"  NATIVE   (weight-set-1, C=0.1):        {native_ok}/{n} ({100*native_ok/max(n,1):.1f}%)   wrong={native_wrong}")
        print(f"  RESCORED (new w*, C*={C_NEW}): {rescored_ok}/{n} ({100*rescored_ok/max(n,1):.1f}%)   wrong={rescored_wrong}")
        if no_log:
            print(f"  no_log/no_entries: {no_log}")
        combined_native_ok += native_ok
        combined_rescored_ok += rescored_ok
        combined_n += n

    print(f"\n{'='*100}\nCOMBINED ({combined_n} cases with scored entries)\n{'='*100}")
    print(f"  NATIVE   (weight-set-1, C=0.1):        {combined_native_ok}/{combined_n} ({100*combined_native_ok/max(combined_n,1):.1f}%)")
    print(f"  RESCORED (new w*, C*={C_NEW}): {combined_rescored_ok}/{combined_n} ({100*combined_rescored_ok/max(combined_n,1):.1f}%)")
    print("\n  (compare to trusted equal-weight baseline HYBRID_C combined: 191/287)")


if __name__ == "__main__":
    main()
