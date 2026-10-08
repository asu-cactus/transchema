"""
evaluate_weights_real.py
===========================
The lookup-based evaluation in analyze_new_weights_all_methods.py silently
drops any case/method whose winning script's OLD score has no match in
score_regression_dataset.csv (an artifact of build_score_regression_dataset.py
sometimes failing to re-run/re-score a given script), shrinking denominators
(e.g. L1 98/100, L4 76/100, L9 97/101) versus the TRUE ground-truth
methodology used by analyze_l1_training_all_methods.py /
analyze_test_script_4_all_methods.py, which actually RE-EXECUTES whatever
script each method selects and validates it for real via run_and_check --
never "unresolved", always a definitive correct/wrong answer, full
denominators (L1 100, L4 86 -- 14 no_log, L9 101).

This script reconciles the two: it uses the CANDIDATE weight vector to
RESCORE and pick which script each of the 5 methods selects (same
rescoring machinery as analyze_new_weights_all_methods.py), but instead of
looking up a cached is_match, it actually RE-EXECUTES the selected script
and validates it for real (run_and_check) -- one real execution per
(case, unique selected script), deduplicated within a case since multiple
methods often pick the same script.

Usage: python3 evaluate_weights_real.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import math
import glob
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")
from analyze_run8_failed_case_scripts import extract_all_scored_scripts, run_and_check
from eval_run8_training import get_node_script
import analyze_new_weights_all_methods as m

FEATURES = ["fd_f1", "avg_col_score_1", "row_count_score", "max_missing_score"]


def flat_hybrid_pick_fixed_freq(entries, lookup_case, freq_by_script, C):
    """Same rescoring logic as analyze_new_weights_all_methods.flat_hybrid_pick_new
    for the SCORE (new_score = w.x under the candidate weights), but freq_i is
    looked up from a FIXED, precomputed table (historical old_score-derived,
    never recomputed under the candidate weights) instead of being
    dynamically re-bucketed from new_score. Returns the SELECTED SCRIPT TEXT
    (for real re-execution)."""
    seen = {}
    for it, kind, script, old_score in entries:
        new_score, is_match, found = m.relook(lookup_case, old_score)
        key = script.strip()
        if key not in seen or new_score > seen[key][1]:
            seen[key] = (script, new_score)

    best_hybrid, best_script = -1e18, None
    for key, (script, new_score) in seen.items():
        f = freq_by_script.get(key, 1)
        hybrid = new_score - C / math.sqrt(f)
        if hybrid > best_hybrid:
            best_hybrid = hybrid
            best_script = script
    return best_script


def process_case_real(length, log_dir, case_num, lookup, freq_lookup, C=0.1):
    d = m.log_dir_for_l1(case_num) if length == 1 else log_dir
    files = sorted(glob.glob(f"{d}/cases_c{case_num}/*.log"))
    if not files:
        return length, case_num, None
    log_file = Path(files[-1])
    lookup_case = lookup.get((str(length), str(case_num)))

    (root, iter_scripts, global_best_script, global_best_score, global_best_is_match,
     total_iters, node_meta, n_miss, n_tot) = m.parse_log_with_new_rewards(log_file, lookup_case)
    if root is None or total_iters == 0:
        return length, case_num, None

    selected = {"BEST_SCORE": global_best_script}
    for name, path_fn in [("OLD_total_reward", m.greedy_tr_path), ("Q_VALUE", m.greedy_q_path),
                           ("LCB_C=0.5", lambda rt: m.greedy_path_lcb(rt, 0.5))]:
        path = path_fn(root)
        leaf = path[-1]
        selected[name] = get_node_script(leaf, iter_scripts)

    entries = extract_all_scored_scripts(log_file)
    freq_by_script = freq_lookup.get((length, case_num), {})
    selected["HYBRID_C=0.1"] = (
        flat_hybrid_pick_fixed_freq(entries, lookup_case, freq_by_script, C) if entries else None
    )

    # Real execution, deduped per unique script text within this case.
    exec_cache = {}

    def real_check(script):
        if not script:
            return False
        key = script.strip()
        if key not in exec_cache:
            ok, note = run_and_check(script, case_num, length=length)
            exec_cache[key] = ok
        return exec_cache[key]

    out = {name: real_check(script) for name, script in selected.items()}
    return length, case_num, out


def evaluate(w_dict, freq_lookup, C=0.1, workers=20):
    lookup = m.load_lookup(weights=w_dict)
    tasks = [(length, log_dir, c) for length, log_dir, n in m.CONFIGS for c in range(n)]
    results = {1: {}, 4: {}, 9: {}}
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_case_real, l, d, c, lookup, freq_lookup, C): (l, c) for l, d, c in tasks}
        for future in as_completed(futures):
            length, c = futures[future]
            try:
                length_r, case_num, out = future.result()
            except Exception as e:
                print(f"L{length} c{c} FAILED: {e}", flush=True)
                continue
            results[length][case_num] = out

    combined = {name: [0, 0] for name in m.METHOD_NAMES}
    per_length = {name: {} for name in m.METHOD_NAMES}
    for length, log_dir, n in m.CONFIGS:
        for c in range(n):
            out = results[length].get(c)
            for name in m.METHOD_NAMES:
                if out is None:
                    continue  # no_log -- excluded from denominator entirely
                pl = per_length[name].setdefault(length, [0, 0])
                pl[1] += 1
                combined[name][1] += 1
                ok = bool(out.get(name))
                combined[name][0] += ok
                pl[0] += ok
    return combined, per_length


def main():
    from fit_hybrid_weights_lp import (
        load_component_lookup, build_case_data,
        build_fixed_freq_by_script, FEATURES as FIT_FEATURES, C_HYBRID,
    )
    from fit_hybrid_c_and_weights_freq_logreg import build_augmented_pairs
    from fit_hybrid_weights_freq_logreg import fit_offset_logreg

    print("Fitting weight-set-1 (existing plain Method C weights, C=0.1 fixed)...")
    weightset1_w = {
        "fd_f1": 0.1241, "avg_col_score_1": 0.2487,
        "row_count_score": 0.3562, "max_missing_score": 0.2710,
    }
    print(f"weight-set-1: {weightset1_w}\n")

    print("Fitting NEW joint (w*, C*) -- 5-dim augmented pairwise LR, "
          "l2=0 (best by held-out from the sweep), 100% of data...")
    comp_lookup = load_component_lookup()
    case_data = build_case_data(comp_lookup)
    Z, y, sw, n_informative = build_augmented_pairs(case_data, case_data.keys())
    offsets = [0.0] * len(y)
    w5vec = fit_offset_logreg(Z, offsets, y, sw, l2=0)
    fit_w, C_fitted = dict(zip(FIT_FEATURES, w5vec[:4])), -w5vec[4]
    print(f"Fitted weights: {fit_w}")
    print(f"Fitted C: {C_fitted:.4f}\n")

    freq_lookup = build_fixed_freq_by_script(comp_lookup)
    equal_w = {f: 0.25 for f in FEATURES}

    print("Evaluating EQUAL-WEIGHT (0.25 each, C=0.1) with REAL re-execution...")
    equal_combined, equal_per_length = evaluate(equal_w, freq_lookup, C=C_HYBRID)
    for name in m.METHOD_NAMES:
        ok, n = equal_combined[name]
        breakdown = "  ".join(f"L{l}={v[0]}/{v[1]}" for l, v in sorted(equal_per_length[name].items()))
        print(f"  {name:<18}: {ok}/{n} ({100*ok/n:.1f}%)   [{breakdown}]")

    print("\nEvaluating WEIGHT-SET-1 (C=0.1 fixed) with REAL re-execution...")
    ws1_combined, ws1_per_length = evaluate(weightset1_w, freq_lookup, C=C_HYBRID)
    for name in m.METHOD_NAMES:
        ok, n = ws1_combined[name]
        breakdown = "  ".join(f"L{l}={v[0]}/{v[1]}" for l, v in sorted(ws1_per_length[name].items()))
        print(f"  {name:<18}: {ok}/{n} ({100*ok/n:.1f}%)   [{breakdown}]")

    print(f"\nEvaluating NEW (w*, C*={C_fitted:.4f}) with REAL re-execution...")
    fit_combined, fit_per_length = evaluate(fit_w, freq_lookup, C=C_fitted)
    for name in m.METHOD_NAMES:
        ok, n = fit_combined[name]
        breakdown = "  ".join(f"L{l}={v[0]}/{v[1]}" for l, v in sorted(fit_per_length[name].items()))
        print(f"  {name:<18}: {ok}/{n} ({100*ok/n:.1f}%)   [{breakdown}]")

    print(f"\n{'='*90}\nCOMPARISON\n{'='*90}")
    print(f"  {'method':<18}  {'equal-weight (C=0.1)':<24}  {'weight-set-1 (C=0.1)':<24}  {'new (w*,C*)':<24}")
    for name in m.METHOD_NAMES:
        e_ok, e_n = equal_combined[name]
        w1_ok, w1_n = ws1_combined[name]
        f_ok, f_n = fit_combined[name]
        print(f"  {name:<18}  {e_ok}/{e_n} ({100*e_ok/e_n:.1f}%){'':<10}  "
              f"{w1_ok}/{w1_n} ({100*w1_ok/w1_n:.1f}%){'':<10}  "
              f"{f_ok}/{f_n} ({100*f_ok/f_n:.1f}%)")


if __name__ == "__main__":
    main()
