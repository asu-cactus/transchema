"""
analyze_l2_o4mini_retry_both_hybrid.py
===========================
For the o4-mini retry of L2's 20 weight-set-1 native-failed cases
(run_l2_weightset1_o4mini_retry.sh), report HYBRID_C=0.1 two ways, same
pattern as rescore_hybrid_l2_weightset1_with_new_wc.py but pointed at the
o4-mini log directory:

  (A) NATIVE   -- score already in the log (weight-set-1's weights, C=0.1,
                  as actually used to drive this o4-mini search).
  (B) RESCORED -- score(i) recomputed from logged raw components under the
                  jointly-fit (w*, C*) from fit_hybrid_c_and_weights_freq_logreg.py.
                  freq stays exactly as this o4-mini search produced it.

Usage: python3 analyze_l2_o4mini_retry_both_hybrid.py
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

LENGTH = 2
LOG_DIR = "logs_langraph/l2_weightset1_o4mini_retry"
FAILED_CASES = [1, 2, 12, 19, 26, 28, 29, 33, 45, 47, 58, 67, 72, 78, 82, 83, 87, 90, 91, 95]


def process_case(case_num: int):
    files = sorted(glob.glob(f"{LOG_DIR}/cases_c{case_num}/*.log"))
    if not files:
        return case_num, None
    log_file = Path(files[-1])
    entries = extract_all_scored_scripts_with_components(log_file)
    if not entries:
        return case_num, None

    plain_entries = [(it, kind, script, old_score) for it, kind, script, old_score, components in entries]
    native_script, native_score = flat_hybrid_pick(plain_entries, 0.1)
    native_ok, _ = run_and_check(native_script, case_num, length=LENGTH) if native_script else (False, "no_script")

    new_script, new_score = rescored_hybrid_pick(entries, W_NEW, C_NEW)
    new_ok, _ = run_and_check(new_script, case_num, length=LENGTH) if new_script else (False, "no_script")

    return case_num, {
        "native": (native_score, native_ok),
        "rescored": (new_score, new_ok),
    }


def main():
    results = {}
    with ProcessPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_case, c): c for c in FAILED_CASES}
        for future in as_completed(futures):
            c = futures[future]
            try:
                case_num, out = future.result()
            except Exception as e:
                print(f"c{c} FAILED: {e}", flush=True)
                continue
            results[case_num] = out
            print(f"c{case_num}: {out}", flush=True)

    print(f"\n{'='*90}\nHYBRID_C=0.1 -- NATIVE vs RESCORED (new w*,C*), L2 o4-mini retry, "
          f"{len(FAILED_CASES)} cases\n{'='*90}")
    n = len([c for c in results if results[c] is not None])
    native_ok = sum(1 for c, out in results.items() if out is not None and out["native"][1])
    rescored_ok = sum(1 for c, out in results.items() if out is not None and out["rescored"][1])
    native_wrong = sorted(c for c, out in results.items() if out is not None and not out["native"][1])
    rescored_wrong = sorted(c for c, out in results.items() if out is not None and not out["rescored"][1])
    no_log = sorted(c for c in FAILED_CASES if results.get(c) is None)

    print(f"  NATIVE   (weight-set-1, C=0.1):        {native_ok}/{n} ({100*native_ok/max(n,1):.1f}%)   wrong={native_wrong}")
    print(f"  RESCORED (new w*, C*={C_NEW}): {rescored_ok}/{n} ({100*rescored_ok/max(n,1):.1f}%)   wrong={rescored_wrong}")
    if no_log:
        print(f"\n  no_log/no_entries: {no_log}")


if __name__ == "__main__":
    main()
