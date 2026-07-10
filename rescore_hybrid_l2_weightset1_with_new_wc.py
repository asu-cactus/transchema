"""
rescore_hybrid_l2_weightset1_with_new_wc.py
===========================
For the L2, 100-case live run (run_l2_weights_100cases.sh, tag=weightset1),
report HYBRID_C=0.1 two ways:

  (A) NATIVE   -- the score already embedded in the log (weight-set-1's own
                  weights, C=0.1 fixed) -- exactly what
                  analyze_l2_weights_100cases_all_methods.py already reports.
  (B) RESCORED -- score(i) recomputed from each event's logged raw
                  components under the SECOND set of tuned weights (the
                  joint w*+C* fit from fit_hybrid_c_and_weights_freq_logreg.py),
                  with C also switched to the fitted C*=5.0728. freq stays
                  exactly as weight-set-1's live search produced it (fixed,
                  historical) -- nothing is re-run, purely log parsing.

Usage: python3 rescore_hybrid_l2_weightset1_with_new_wc.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
import math
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import run_and_check
from analyze_test_script_4_all_methods import flat_hybrid_pick
from rescore_hybrid_weightset1_with_weightset2 import extract_all_scored_scripts_with_components, rescored_hybrid_pick
from rescore_hybrid_weightset1_with_new_wc import W_NEW, C_NEW

LENGTH = 2
N_CASES = 100
LOG_DIR = f"logs_langraph/l2_weights_100cases_weightset1"


def process_case(case_num: int):
    files = sorted(glob.glob(f"{LOG_DIR}/cases_c{case_num}/*.log"))
    if not files:
        return case_num, None
    log_file = Path(files[-1])
    entries = extract_all_scored_scripts_with_components(log_file)
    if not entries:
        return case_num, None

    # (A) native: score already in the log (weight-set-1, C=0.1)
    plain_entries = [(it, kind, script, old_score) for it, kind, script, old_score, components in entries]
    native_script, native_score = flat_hybrid_pick(plain_entries, 0.1)
    native_ok, _ = run_and_check(native_script, case_num, length=LENGTH) if native_script else (False, "no_script")

    # (B) rescored: new (w*, C*) applied to logged raw components, freq unchanged
    new_script, new_score = rescored_hybrid_pick(entries, W_NEW, C_NEW)
    new_ok, _ = run_and_check(new_script, case_num, length=LENGTH) if new_script else (False, "no_script")

    return case_num, {
        "native": (native_score, native_ok),
        "rescored": (new_score, new_ok),
    }


def main():
    print(f"New (w*, C*): {W_NEW}, C={C_NEW}\n")
    results = {}
    cases = list(range(N_CASES))
    for batch_start in range(0, len(cases), 20):
        batch = cases[batch_start:batch_start + 20]
        print(f"--- batch {batch[0]}-{batch[-1]} ---", flush=True)
        with ProcessPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(process_case, c): c for c in batch}
            for future in as_completed(futures):
                c = futures[future]
                try:
                    case_num, out = future.result()
                except Exception as e:
                    print(f"c{c} FAILED: {e}", flush=True)
                    continue
                results[case_num] = out
                print(f"c{case_num}: {out}", flush=True)

    print(f"\n{'='*90}\nHYBRID_C=0.1 -- NATIVE vs RESCORED (new w*,C*), L2, {N_CASES} cases\n{'='*90}")
    n = len([c for c in results if results[c] is not None])
    native_ok = sum(1 for c, out in results.items() if out is not None and out["native"][1])
    rescored_ok = sum(1 for c, out in results.items() if out is not None and out["rescored"][1])
    native_wrong = sorted(c for c, out in results.items() if out is not None and not out["native"][1])
    rescored_wrong = sorted(c for c, out in results.items() if out is not None and not out["rescored"][1])
    no_log = sorted(c for c in results if results[c] is None)

    print(f"  NATIVE   (weight-set-1, C=0.1):        {native_ok}/{n} ({100*native_ok/max(n,1):.1f}%)   wrong={native_wrong}")
    print(f"  RESCORED (new w*, C*={C_NEW}): {rescored_ok}/{n} ({100*rescored_ok/max(n,1):.1f}%)   wrong={rescored_wrong}")
    if no_log:
        print(f"\n  no_log/no_entries: {no_log}")


if __name__ == "__main__":
    main()
