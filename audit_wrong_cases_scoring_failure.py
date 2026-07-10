"""
audit_wrong_cases_scoring_failure.py
===========================
For the 21 cases where A(b) (weight-set-1 live search + new (w*,C*) FAS
rescoring) picked a wrong script, determine which are:
  - SCORING FAILURE (mixed_competitive): a correct script exists SOMEWHERE
    in that case's log among every unique script ever produced, but hybrid
    selection just didn't rank it top -- fixable in principle by a better
    scoring function.
  - NO CORRECT AVAILABLE: no correct script was ever generated anywhere in
    the search for that case -- not fixable by any scoring/weight change,
    a search/candidate-generation gap instead.

Real-executes EVERY unique script per case against TEST data (run_and_check)
to get ground truth, not just the one HYBRID_C happened to pick.

Usage: python3 audit_wrong_cases_scoring_failure.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
import math
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_run8_failed_case_scripts import run_and_check
from rescore_hybrid_weightset1_with_weightset2 import extract_all_scored_scripts_with_components
from rescore_hybrid_weightset1_with_new_wc import W_NEW, C_NEW
from fit_hybrid_weights_lp import FEATURES

WRONG_CASES = {
    1: [54, 64, 81, 86, 94],
    4: [11, 13, 19, 20, 28, 48, 53, 97],
    9: [15, 24, 45, 46, 68, 70, 73, 44],
}


def audit_case(length, case_num):
    log_dir = f"logs_langraph/score_weights_60cases_weightset1_l{length}"
    files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
    if not files:
        return length, case_num, {"status": "no_log"}
    entries = extract_all_scored_scripts_with_components(Path(files[-1]))
    if not entries:
        return length, case_num, {"status": "no_scored_entries"}

    freq_map = {}
    for it, kind, script, old_score, components in entries:
        r = round(old_score, 4)
        freq_map[r] = freq_map.get(r, 0) + 1

    seen = {}
    for it, kind, script, old_score, components in entries:
        key = script.strip()
        if key not in seen or old_score > seen[key][1]:
            seen[key] = (script, old_score, components)

    # Real-execute every unique script for ground truth.
    scored = []
    for key, (script, old_score, components) in seen.items():
        new_score = sum(W_NEW[f] * components[f] for f in FEATURES) if components else old_score
        fr = freq_map.get(round(old_score, 4), 1)
        hybrid = new_score - C_NEW / math.sqrt(fr)
        ok, note = run_and_check(script, case_num, length=length)
        scored.append({"script": script, "old_score": old_score, "new_score": new_score,
                        "freq": fr, "hybrid": hybrid, "is_correct": ok})

    scored.sort(key=lambda r: -r["hybrid"])
    picked = scored[0]
    n_correct = sum(1 for r in scored if r["is_correct"])

    if n_correct == 0:
        status = "no_correct_available"
    else:
        status = "scoring_failure"  # a correct script existed but wasn't picked

    best_correct = max((r for r in scored if r["is_correct"]), key=lambda r: r["hybrid"], default=None)

    return length, case_num, {
        "status": status,
        "n_unique_scripts": len(scored),
        "n_correct_scripts": n_correct,
        "picked_hybrid": picked["hybrid"],
        "picked_new_score": picked["new_score"],
        "picked_freq": picked["freq"],
        "best_correct_hybrid": best_correct["hybrid"] if best_correct else None,
        "best_correct_new_score": best_correct["new_score"] if best_correct else None,
        "best_correct_freq": best_correct["freq"] if best_correct else None,
        "rank_of_best_correct": (sorted(scored, key=lambda r: -r["hybrid"]).index(best_correct) + 1) if best_correct else None,
    }


def main():
    tasks = [(length, c) for length, cases in WRONG_CASES.items() for c in cases]
    results = {}
    with ProcessPoolExecutor(max_workers=21) as executor:
        futures = {executor.submit(audit_case, l, c): (l, c) for l, c in tasks}
        for future in as_completed(futures):
            l, c = futures[future]
            try:
                length, case_num, out = future.result()
            except Exception as e:
                print(f"L{l} c{c} FAILED: {e}", flush=True)
                continue
            results[(length, case_num)] = out
            print(f"L{length} c{case_num} done: {out.get('status')}", flush=True)

    print(f"{'='*100}\nAudit of 21 wrong A(b) cases: scoring failure vs no-correct-available\n{'='*100}\n")

    scoring_failures = []
    no_correct = []
    for length in sorted(WRONG_CASES):
        for c in WRONG_CASES[length]:
            out = results.get((length, c))
            if out is None:
                continue
            status = out["status"]
            if status == "no_scored_entries" or status == "no_log":
                print(f"L{length} c{c}: {status} (nothing to check)")
                no_correct.append((length, c))
                continue
            if status == "no_correct_available":
                print(f"L{length} c{c}: NO_CORRECT_AVAILABLE "
                      f"({out['n_unique_scripts']} unique scripts tried, 0 correct)")
                no_correct.append((length, c))
            else:
                print(f"L{length} c{c}: SCORING_FAILURE "
                      f"({out['n_correct_scripts']}/{out['n_unique_scripts']} unique scripts correct) -- "
                      f"picked hybrid={out['picked_hybrid']:.4f} (new_score={out['picked_new_score']:.4f}, freq={out['picked_freq']}), "
                      f"best correct hybrid={out['best_correct_hybrid']:.4f} "
                      f"(new_score={out['best_correct_new_score']:.4f}, freq={out['best_correct_freq']}, "
                      f"ranked #{out['rank_of_best_correct']} of {out['n_unique_scripts']})")
                scoring_failures.append((length, c))

    print(f"\n{'='*100}\nSUMMARY\n{'='*100}")
    print(f"  SCORING FAILURE (fixable in principle):  {len(scoring_failures)}  {scoring_failures}")
    print(f"  NO CORRECT AVAILABLE (search gap, not fixable by scoring): {len(no_correct)}  {no_correct}")


if __name__ == "__main__":
    main()
