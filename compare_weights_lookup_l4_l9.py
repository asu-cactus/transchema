"""
compare_weights_lookup_l4_l9.py
==================================
Answers: "if we apply the CSV-lookup approach uniformly, does accuracy
improve with the new weights?" -- for that we need an apples-to-apples
comparison, not (real-execution equal-weight baseline) vs (lookup-based
new-weight numbers), since the lookup method has its own ~13% miss-rate
noise independent of which weights it's given.

So: run the SAME lookup-based tree-substitution method
(analyze_new_weights_all_methods.parse_log_with_new_rewards) TWICE on the
same test_script_4_l4 / test_script_4_l9 logs -- once with EQUAL weights
(0.25 each, the current formula), once with the NEW pairwise-LR weights --
and compare on the same basis. This isolates the effect of reweighting from
the lookup shortcut's own inherent noise.

Usage: python3 compare_weights_lookup_l4_l9.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")

from analyze_new_weights_all_methods import (
    load_lookup, process_case, METHOD_NAMES, CONFIGS,
)

EQUAL_W = {"fd_f1": 0.25, "avg_col_score_1": 0.25, "row_count_score": 0.25, "max_missing_score": 0.25}
NEW_W = {"fd_f1": 0.1241, "avg_col_score_1": 0.2487, "row_count_score": 0.3562, "max_missing_score": 0.2710}

TARGET_CONFIGS = [c for c in CONFIGS if c[0] in (4, 9)]  # L4, L9 only -- "that experiment"


def run_all(weights_label, weights):
    lookup = load_lookup(weights=weights)
    tasks = [(length, log_dir, c) for length, log_dir, n in TARGET_CONFIGS for c in range(n)]
    results = {4: {}, 9: {}}
    with ProcessPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_case, l, d, c, lookup): (l, c) for l, d, c in tasks}
        for future in as_completed(futures):
            length, c = futures[future]
            try:
                length_r, case_num, out = future.result()
            except Exception as e:
                print(f"[{weights_label}] L{length} c{c} FAILED: {e}", flush=True)
                continue
            results[length][case_num] = out
    return results


def summarize(results, length, n):
    cases = list(range(n))
    row = {}
    for name in METHOD_NAMES:
        n_ok = n_known = 0
        for c in cases:
            out = results[length].get(c)
            if out is None:
                continue
            methods, n_miss, n_tot = out
            score, is_match = methods[name]
            if is_match is None:
                continue
            n_known += 1
            n_ok += bool(is_match)
        row[name] = (n_ok, n_known)
    return row


def main():
    print("Running EQUAL-weight lookup pass...", flush=True)
    eq_results = run_all("EQUAL", EQUAL_W)
    print("Running NEW-weight lookup pass...", flush=True)
    new_results = run_all("NEW", NEW_W)

    for length, log_dir, n in TARGET_CONFIGS:
        eq_row = summarize(eq_results, length, n)
        new_row = summarize(new_results, length, n)
        print(f"\n{'='*80}\nL{length} -- lookup-based comparison (equal weights vs new weights)\n{'='*80}")
        print(f"{'Method':<18}{'Equal-weight (lookup)':<26}{'New-weight (lookup)':<26}{'Delta':<10}")
        for name in METHOD_NAMES:
            eo, ek = eq_row[name]
            no, nk = new_row[name]
            eq_pct = 100 * eo / ek if ek else 0.0
            new_pct = 100 * no / nk if nk else 0.0
            delta = new_pct - eq_pct
            print(f"{name:<18}{f'{eo}/{ek} ({eq_pct:.1f}%)':<26}{f'{no}/{nk} ({new_pct:.1f}%)':<26}{delta:+.1f}pp")


if __name__ == "__main__":
    main()
