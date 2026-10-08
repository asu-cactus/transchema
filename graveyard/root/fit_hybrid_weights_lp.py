"""
fit_hybrid_weights_lp.py
===========================
Fits score_1 weights (fd_f1, avg_col_score_1, row_count_score,
max_missing_score) to maximize accuracy of a frequency-adjusted score:

    hybrid_i = w.x_i - C / sqrt(freq_i)

where freq_i is a FIXED, known constant per unique script -- computed once
by walking each case's MCTS log and counting how many scored events (across
every iteration, sim and critique, not deduplicated) land on that script's
own logged score. freq_i does NOT depend on w and is never recomputed --
we're not trying to track what the live search's own HYBRID_C mechanism
would do under new weights, just directly maximizing "does argmax_i
hybrid_i pick the correct script" using the frequency numbers each case
already has.

Method: for every case with both a correct and a wrong unique script, and
every such (correct, wrong) pair, want hybrid_r > hybrid_q:

    w.x_r - C/sqrt(freq_r)  >  w.x_q - C/sqrt(freq_q)
    w.(x_r - x_q)           >  C.(1/sqrt(freq_r) - 1/sqrt(freq_q))

-- linear in w with a known per-pair constant offset. Solved as an LP
(same max-margin ranking structure as the plain BEST_SCORE fit, margin=1,
per-case-normalized slack objective, w >= 0).

Fit across L1+L4+L9 combined.

Usage: python3 fit_hybrid_weights_lp.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import csv
import glob
import math
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, ".")
from analyze_run8_failed_case_scripts import extract_all_scored_scripts

FEATURES = ["fd_f1", "avg_col_score_1", "row_count_score", "max_missing_score"]
EQUAL_W = np.array([0.25, 0.25, 0.25, 0.25])
C_HYBRID = 0.1

PILOT_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_pilot20"
BATCH_LOG_DIR = "logs_langraph/rag_det_score_run9_l1_batch_20to100"

CONFIGS = [
    (1, None, 100),
    (4, "logs_langraph/test_script_4_l4", 100),
    (9, "logs_langraph/test_script_4_l9", 101),
]


def log_dir_for_l1(case_num: int) -> str:
    return PILOT_LOG_DIR if case_num < 20 else BATCH_LOG_DIR


def load_component_lookup(path="score_regression_dataset.csv"):
    """(length, case_num, iter, kind) -> (x_vec, is_match), keyed by exact
    script identity (not score value, which collides across unrelated scripts)."""
    lookup = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r["train_run_ok"] != "True":
                continue
            if any(r[k] == "" for k in FEATURES):
                continue
            if r["is_match"] not in ("True", "False"):
                continue
            key = (r["length"], r["case_num"], r["iter"], r["kind"])
            x = np.array([float(r[k]) for k in FEATURES])
            is_match = r["is_match"] == "True"
            lookup[key] = (x, is_match)
    return lookup


def build_case_data(comp_lookup):
    """For every case: list of (x_vec, is_match, freq) for each UNIQUE script,
    where freq is a FIXED count -- how many scored events in the case's full
    log (every iteration, not deduplicated) landed on that script's own
    logged score."""
    case_data = {}
    n_lookup_miss = n_lookup_total = 0

    for length, log_dir, n in CONFIGS:
        for case_num in range(n):
            d = log_dir_for_l1(case_num) if length == 1 else log_dir
            files = sorted(glob.glob(f"{d}/cases_c{case_num}/*.log"))
            if not files:
                continue
            log_file = Path(files[-1])
            entries = extract_all_scored_scripts(log_file)
            if not entries:
                continue

            first_seen = {}
            for it, kind, script, old_score in entries:
                key_s = script.strip()
                if key_s not in first_seen:
                    first_seen[key_s] = (it, kind, old_score)

            text_to_x = {}
            for key_s, (it, kind, old_score) in first_seen.items():
                entry = comp_lookup.get((str(length), str(case_num), str(it), kind))
                if entry is not None:
                    x, is_match = entry
                    text_to_x[key_s] = (x, is_match, old_score)

            if not text_to_x:
                continue

            # freq: count every raw occurrence (any script, resolved or not)
            # whose logged score rounds the same as this script's own score --
            # a fixed historical fact read straight from the log. old_score is
            # already known directly from the log for every event, so no CSV
            # resolution is needed here (that's only needed for x/is_match).
            freq_map = {}
            for it, kind, script, old_score in entries:
                n_lookup_total += 1
                if script.strip() not in text_to_x:
                    n_lookup_miss += 1
                s = round(old_score, 4)
                freq_map[s] = freq_map.get(s, 0) + 1

            case_list = [
                (x, is_match, freq_map.get(round(old_score, 4), 1))
                for x, is_match, old_score in text_to_x.values()
            ]
            case_data[(length, case_num)] = case_list

    print(f"Lookup miss rate: {n_lookup_miss}/{max(n_lookup_total,1)} "
          f"({100*n_lookup_miss/max(n_lookup_total,1):.1f}%) scored events had no CSV match")
    return case_data


def build_fixed_freq_by_script(comp_lookup):
    """(length, case_num) -> {script_text_stripped: freq}. Same fixed,
    historical-old_score-derived freq as build_case_data, but keyed by the
    actual script text so callers that need to look up freq by script
    (rather than by x_vec) can use it directly."""
    result = {}
    for length, log_dir, n in CONFIGS:
        for case_num in range(n):
            d = log_dir_for_l1(case_num) if length == 1 else log_dir
            files = sorted(glob.glob(f"{d}/cases_c{case_num}/*.log"))
            if not files:
                continue
            log_file = Path(files[-1])
            entries = extract_all_scored_scripts(log_file)
            if not entries:
                continue

            first_seen = {}
            for it, kind, script, old_score in entries:
                key_s = script.strip()
                if key_s not in first_seen:
                    first_seen[key_s] = (it, kind, old_score)

            text_to_x = {}
            for key_s, (it, kind, old_score) in first_seen.items():
                entry = comp_lookup.get((str(length), str(case_num), str(it), kind))
                if entry is not None:
                    text_to_x[key_s] = old_score

            if not text_to_x:
                continue

            freq_map = {}
            for it, kind, script, old_score in entries:
                s = round(old_score, 4)
                freq_map[s] = freq_map.get(s, 0) + 1

            result[(length, case_num)] = {
                key_s: freq_map.get(round(old_score, 4), 1)
                for key_s, old_score in text_to_x.items()
            }
    return result


def build_pairs(case_data):
    pair_rows = []
    n_informative = 0
    for key, case_list in case_data.items():
        correct = [(x, freq) for x, is_match, freq in case_list if is_match]
        wrong = [(x, freq) for x, is_match, freq in case_list if not is_match]
        if not correct or not wrong:
            continue
        n_informative += 1
        n_pairs_this_case = len(correct) * len(wrong)
        for x_r, freq_r in correct:
            for x_q, freq_q in wrong:
                offset = C_HYBRID * (1.0 / math.sqrt(freq_r) - 1.0 / math.sqrt(freq_q))
                pair_rows.append((x_r - x_q, offset, n_pairs_this_case))
    return pair_rows, n_informative


def solve_lp(pair_rows):
    n = len(pair_rows)
    n_vars = 4 + n
    weights_obj = np.array([1.0 / row[2] for row in pair_rows])
    c = np.concatenate([np.zeros(4), weights_obj])

    A_ub = np.zeros((n, n_vars))
    b_ub = np.zeros(n)
    for i, (dx, offset, _) in enumerate(pair_rows):
        A_ub[i, :4] = -dx
        A_ub[i, 4 + i] = -1.0
        b_ub[i] = -(1.0 + offset)

    bounds = [(0, None)] * n_vars
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(f"LP failed: {res.message}")
    return res.x[:4]


def eval_fixed_freq_accuracy(w, case_data):
    """argmax_i [w.x_i - C/sqrt(freq_i)] correctness, using the SAME fixed
    freq_i as fitting -- self-consistent, no recomputation. Returns
    (n_ok, n_total, per_length dict)."""
    per_length = {}
    n_ok = n_total = 0
    for (length, case_num), case_list in case_data.items():
        best = max(case_list, key=lambda t: float(np.dot(w, t[0])) - C_HYBRID / math.sqrt(t[2]))
        ok = best[1]
        n_total += 1
        n_ok += bool(ok)
        pl = per_length.setdefault(length, [0, 0])
        pl[1] += 1
        pl[0] += bool(ok)
    return n_ok, n_total, per_length


def main():
    comp_lookup = load_component_lookup()
    print(f"Component lookup covers {len(comp_lookup)} cases")

    case_data = build_case_data(comp_lookup)
    print(f"Built per-case data for {len(case_data)} cases")

    pair_rows, n_informative = build_pairs(case_data)
    print(f"{len(pair_rows)} pairwise constraints across {n_informative} informative cases")

    if not pair_rows:
        print("No informative pairs -- aborting.")
        return

    w = solve_lp(pair_rows)
    print(f"\nFitted weights (frequency-adjusted, fixed freq, L1+L4+L9 combined):")
    for f, v in zip(FEATURES, w):
        print(f"  {f} = {v:.4f}")
    total = np.sum(w)
    if total > 0:
        print("Normalized (sum=1):", {f: round(v, 4) for f, v in zip(FEATURES, w / total)})

    print(f"\n{'='*70}\nFixed-freq accuracy: argmax_i [w.x_i - C/sqrt(freq_i)] correctness\n{'='*70}")
    equal_ok, n, equal_pl = eval_fixed_freq_accuracy(EQUAL_W, case_data)
    fit_ok, _, fit_pl = eval_fixed_freq_accuracy(w, case_data)
    print(f"Equal-weight (0.25 each): {equal_ok}/{n} ({100*equal_ok/n:.1f}%)")
    for l in sorted(equal_pl, key=int):
        ok, nn = equal_pl[l]
        print(f"  L{l}: {ok}/{nn} ({100*ok/nn:.1f}%)")
    print(f"Fitted weights:           {fit_ok}/{n} ({100*fit_ok/n:.1f}%)")
    for l in sorted(fit_pl, key=int):
        ok, nn = fit_pl[l]
        print(f"  L{l}: {ok}/{nn} ({100*ok/nn:.1f}%)")


if __name__ == "__main__":
    main()
