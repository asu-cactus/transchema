"""
evaluate_mixed_weights_real.py
===========================
score_1 currently plays two roles at once: it's the MCTS REWARD signal
(what BEST_SCORE / OLD_total_reward / Q_VALUE / LCB_C=0.5 are all built
from, via tree backprop/traversal), and it's also the `score(i)` term
inside the Frequency Adjusted Score (HYBRID_C):
`hybrid(i) = score(i) - C/sqrt(freq_i)`. These don't have to use the same
weight vector -- a weight vector optimized for one role isn't necessarily
best for the other (this is exactly why plain Method C's weights, fit for
best-score-style ranking, hurt HYBRID_C when applied there too).

This script compares, on a SMALL HELD-OUT SUBSET of cases (real script
re-execution, not cached lookup):

  Weight-set-1 (reward):  existing plain Method C weights (fit for
    best-score-style ranking, ignoring frequency -- SCORE_WEIGHTS_ANALYSIS.md
    Method C): fd_f1=0.1241, avg_col_score_1=0.2487, row_count_score=0.3562,
    max_missing_score=0.2710.
  Weight-set-2 (FAS):  the frequency-aware pairwise-logistic-regression fit
    (fit_hybrid_weights_freq_logreg.py), refit here on the TRAIN-only split
    (220 cases) so it has never seen the held-out subset being evaluated.

  (1) MIXED   -- reward computed with weight-set-1, HYBRID_C's score(i)
                 computed with weight-set-2 (freq stays fixed/historical
                 either way).
  (2) UNIFORM -- weight-set-2 used for both roles.
  (0) EQUAL   -- equal-weight (0.25 each) for both roles, for context.

Usage: python3 evaluate_mixed_weights_real.py
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
from evaluate_weights_real import flat_hybrid_pick_fixed_freq, FEATURES

from fit_hybrid_weights_lp import (
    load_component_lookup, build_case_data, build_fixed_freq_by_script,
    FEATURES as FIT_FEATURES, C_HYBRID,
)
from fit_hybrid_weights_freq_logreg import split_cases, build_pairs, fit_offset_logreg

W_REWARD = {  # existing plain Method C weights (no frequency awareness)
    "fd_f1": 0.1241, "avg_col_score_1": 0.2487,
    "row_count_score": 0.3562, "max_missing_score": 0.2710,
}
EQUAL_W = {f: 0.25 for f in FEATURES}


def process_case_real(length, log_dir, case_num, lookup_reward, lookup_fas, freq_lookup):
    d = m.log_dir_for_l1(case_num) if length == 1 else log_dir
    files = sorted(glob.glob(f"{d}/cases_c{case_num}/*.log"))
    if not files:
        return length, case_num, None
    log_file = Path(files[-1])
    lookup_case_reward = lookup_reward.get((str(length), str(case_num)))
    lookup_case_fas = lookup_fas.get((str(length), str(case_num)))

    (root, iter_scripts, global_best_script, global_best_score, global_best_is_match,
     total_iters, node_meta, n_miss, n_tot) = m.parse_log_with_new_rewards(log_file, lookup_case_reward)
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
        flat_hybrid_pick_fixed_freq(entries, lookup_case_fas, freq_by_script, 0.1) if entries else None
    )

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


def evaluate(w_reward, w_fas, freq_lookup, case_subset, workers=20):
    """case_subset: iterable of (length, case_num) to restrict to."""
    lookup_reward = m.load_lookup(weights=w_reward)
    lookup_fas = m.load_lookup(weights=w_fas)
    log_dir_by_length = {length: log_dir for length, log_dir, n in m.CONFIGS}
    tasks = [(length, log_dir_by_length[length], c) for length, c in case_subset]

    results = {1: {}, 4: {}, 9: {}}
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(process_case_real, l, d, c, lookup_reward, lookup_fas, freq_lookup): (l, c)
            for l, d, c in tasks
        }
        for future in as_completed(futures):
            length, c = futures[future]
            try:
                _, case_num, out = future.result()
            except Exception as e:
                print(f"L{length} c{c} FAILED: {e}", flush=True)
                continue
            results[length][case_num] = out

    combined = {name: [0, 0] for name in m.METHOD_NAMES}
    per_length = {name: {} for name in m.METHOD_NAMES}
    for length, c in case_subset:
        out = results[length].get(c)
        for name in m.METHOD_NAMES:
            if out is None:
                continue
            pl = per_length[name].setdefault(length, [0, 0])
            pl[1] += 1
            combined[name][1] += 1
            ok = bool(out.get(name))
            combined[name][0] += ok
            pl[0] += ok
    return combined, per_length


def print_result(name, combined, per_length):
    for method in m.METHOD_NAMES:
        ok, n = combined[method]
        breakdown = "  ".join(f"L{l}={v[0]}/{v[1]}" for l, v in sorted(per_length[method].items()))
        print(f"  {method:<18}: {ok}/{n} ({100*ok/max(n,1):.1f}%)   [{breakdown}]")


def main():
    comp_lookup = load_component_lookup()
    case_data = build_case_data(comp_lookup)
    freq_lookup = build_fixed_freq_by_script(comp_lookup)

    train_keys, test_keys = split_cases(case_data)
    print(f"Train cases: {len(train_keys)}, held-out (small subset) cases: {len(test_keys)}\n")

    print("Refitting weight-set-2 (FAS, frequency-aware pairwise LR, L2=100) "
          "on TRAIN-only split (never sees the held-out subset below)...")
    Z, offsets, y, sw, n_informative = build_pairs(case_data, train_keys, C_HYBRID)
    w_fas_vec = fit_offset_logreg(Z, offsets, y, sw, l2=100)
    w_fas = dict(zip(FIT_FEATURES, w_fas_vec))
    print(f"Weight-set-2 (FAS):     {w_fas}")
    print(f"Weight-set-1 (reward):  {W_REWARD}\n")

    case_subset = sorted(test_keys)

    print(f"{'='*70}\n(0) EQUAL-WEIGHT for both roles, held-out subset ({len(case_subset)} cases)\n{'='*70}")
    equal_combined, equal_per_length = evaluate(EQUAL_W, EQUAL_W, freq_lookup, case_subset)
    print_result("equal", equal_combined, equal_per_length)

    print(f"\n{'='*70}\n(1) MIXED -- reward=weight-set-1, FAS=weight-set-2\n{'='*70}")
    mixed_combined, mixed_per_length = evaluate(W_REWARD, w_fas, freq_lookup, case_subset)
    print_result("mixed", mixed_combined, mixed_per_length)

    print(f"\n{'='*70}\n(2) UNIFORM -- weight-set-2 for both roles\n{'='*70}")
    uniform_combined, uniform_per_length = evaluate(w_fas, w_fas, freq_lookup, case_subset)
    print_result("uniform", uniform_combined, uniform_per_length)

    print(f"\n{'='*70}\nCOMPARISON (held-out subset, {len(case_subset)} cases)\n{'='*70}")
    print(f"  {'method':<18}  {'equal':<14}  {'mixed':<14}  {'uniform':<14}")
    for name in m.METHOD_NAMES:
        e_ok, e_n = equal_combined[name]
        mx_ok, mx_n = mixed_combined[name]
        u_ok, u_n = uniform_combined[name]
        print(f"  {name:<18}  {e_ok}/{e_n} ({100*e_ok/max(e_n,1):.1f}%)   "
              f"{mx_ok}/{mx_n} ({100*mx_ok/max(mx_n,1):.1f}%)   "
              f"{u_ok}/{u_n} ({100*u_ok/max(u_n,1):.1f}%)")


if __name__ == "__main__":
    main()
