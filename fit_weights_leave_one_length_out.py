"""
fit_weights_leave_one_length_out.py
======================================
Fits pairwise-ranking-logistic-regression weights (Method C from
SCORE_WEIGHTS_ANALYSIS.md, generalized to the flat leaf-feature set) against
scraped_scripts/scraped_scripts_scores.csv.

Feature vector x(s) = 16 leaf signals produced by collect_scraped_script_scores.py:
  precision, recall  (fd_f1's two halves)
  avg_float_js, avg_float_range
  avg_int_js, avg_int_range, avg_int_nunique, avg_int_missing
  avg_id_nunique, avg_id_missing
  avg_cat_prop, avg_cat_nunique, avg_cat_missing
  avg_date_score
  row_count_score, max_missing_score
A column-type signal missing from a given script's table (e.g. no id columns)
is imputed as 0 -- "no columns of this type" rather than "scored perfectly."

For every length L in {1,2,3,4,5,9}: train the pairwise ranking model on every
OTHER length's (case, script) pairs, then evaluate the fitted weights on L's
own held-out cases only. This is a leave-one-length-out generalization test
(does a weighting learned from other problem lengths transfer to a new one),
not a within-length random split -- producing one weight vector per length,
6 total.

For every case, "correct" = is_match True on the TEST-side autopipeline
validation (script rewritten to read test_N.csv, compared to target.csv).

Usage: python3 fit_weights_leave_one_length_out.py [--csv PATH]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import argparse
import csv

import numpy as np
from sklearn.linear_model import LogisticRegression

LENGTHS = ["1", "2", "3", "4", "5", "9"]

LEAF_FEATURES = [
    "precision", "recall",
    "avg_float_js", "avg_float_range",
    "avg_int_js", "avg_int_range", "avg_int_nunique", "avg_int_missing",
    "avg_id_nunique", "avg_id_missing",
    "avg_cat_prop", "avg_cat_nunique", "avg_cat_missing",
    "avg_date_score",
    "row_count_score", "max_missing_score",
]

# The existing equal-weight 4-component formula, already baked into the CSV's
# own score_1 column -- used only as a reference baseline in the eval tables.
BASELINE_COL = "score_1"

# Nested/grouped score formalization discussed alongside the flat fit:
#   top     = fd, col, row, miss
#   fd      = precision, recall
#   col     = float, int, id, cat, date  (a "type mix" over ColumnScore)
#   float   = js, range
#   int     = js, range, nunique, missing
#   id      = nunique, missing
#   cat     = prop, nunique, missing
#   date    = avg_date_score alone (the underlying scoring code doesn't expose
#             separate js/range for dates -- see WEIGHT_TUNING_LEAF_FEATURES.md)
# No new fitting happens for this -- it's a read-out of the SAME flat
# pairwise-LR coefficients already fit above, grouped and normalized within
# each group purely for interpretability (dividing by a group's coefficient
# sum only cleanly reads as "share of that group" when every coefficient in
# it has the same sign -- flagged per group below when that's not the case).
WITHIN_TYPE_GROUPS = {
    "float": ["avg_float_js", "avg_float_range"],
    "int": ["avg_int_js", "avg_int_range", "avg_int_nunique", "avg_int_missing"],
    "id": ["avg_id_nunique", "avg_id_missing"],
    "cat": ["avg_cat_prop", "avg_cat_nunique", "avg_cat_missing"],
    "date": ["avg_date_score"],
}
FD_GROUP = ["precision", "recall"]
TOP_GROUPS = {
    "fd": FD_GROUP,
    "col": [f for feats in WITHIN_TYPE_GROUPS.values() for f in feats],
    "row": ["row_count_score"],
    "miss": ["max_missing_score"],
}


def _float_or(v, default=0.0):
    return float(v) if v not in ("", None) else default


def load_rows(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    # fd_f1 is only ever populated once the TRAIN-side scoring call actually
    # completed -- catches both train_run_ok=False rows and the rarer case
    # where the script ran but scoring itself raised (train_run_ok stays True
    # but every score column is blank).
    usable = [r for r in rows if r.get("fd_f1", "") != "" and r.get("is_match") in ("True", "False")]
    for r in usable:
        r["_x"] = np.array([_float_or(r[k]) for k in LEAF_FEATURES])
        r["_y"] = 1 if r["is_match"] == "True" else 0
        r["_baseline"] = _float_or(r.get(BASELINE_COL))
    return usable


def group_by_case(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r["length"], r["case_num"]), []).append(r)
    return groups


def fit_pairwise(train_groups):
    """One (correct, wrong) pair per case -> two symmetric training examples
    each (z = x_pos - x_neg, label 1; z = x_neg - x_pos, label 0)."""
    diffs = []
    for rows in train_groups.values():
        pos = [r for r in rows if r["_y"] == 1]
        neg = [r for r in rows if r["_y"] == 0]
        for p in pos:
            for n in neg:
                diffs.append(p["_x"] - n["_x"])
                diffs.append(n["_x"] - p["_x"])
    if not diffs:
        return None
    Z = np.stack(diffs)
    y = np.array([1, 0] * (len(diffs) // 2))
    clf = LogisticRegression(fit_intercept=False, max_iter=5000)
    clf.fit(Z, y)
    return clf.coef_[0]


def normalize_group(feat_val, feat_names):
    """Sum the raw coefficients for feat_names and divide each by that sum.
    Returns (normalized_dict, group_sum, mixed_sign). mixed_sign=True means
    not every coefficient in this group has the same sign, so "share of
    group" is not a clean percentage read for this particular group (flagged
    in the report rather than hidden)."""
    vals = {f: feat_val[f] for f in feat_names}
    total = sum(vals.values())
    mixed_sign = any(v < 0 for v in vals.values()) and any(v > 0 for v in vals.values())
    if abs(total) < 1e-9:
        return {f: float("nan") for f in feat_names}, total, mixed_sign
    return {f: v / total for f, v in vals.items()}, total, mixed_sign


def grouped_view(w):
    """Read out the nested/grouped formalization from a flat weight vector
    w (ordered per LEAF_FEATURES) -- no new fitting, just regrouping +
    within-group normalization of the already-fit flat coefficients."""
    feat_val = dict(zip(LEAF_FEATURES, w))

    top_sums = {name: sum(feat_val[f] for f in feats) for name, feats in TOP_GROUPS.items()}
    top_norm, _, top_mixed = normalize_group(top_sums, list(TOP_GROUPS.keys()))

    fd_norm, _, fd_mixed = normalize_group(feat_val, FD_GROUP)

    type_sums = {name: sum(feat_val[f] for f in feats) for name, feats in WITHIN_TYPE_GROUPS.items()}
    type_norm, _, type_mixed = normalize_group(type_sums, list(WITHIN_TYPE_GROUPS.keys()))

    within_type_norm = {}
    within_type_mixed = {}
    for name, feats in WITHIN_TYPE_GROUPS.items():
        if len(feats) == 1:
            within_type_norm[name] = {feats[0]: 1.0}
            within_type_mixed[name] = False
            continue
        norm, _, mixed = normalize_group(feat_val, feats)
        within_type_norm[name] = norm
        within_type_mixed[name] = mixed

    return {
        "top": (top_norm, top_mixed),
        "fd": (fd_norm, fd_mixed),
        "typemix": (type_norm, type_mixed),
        "within_type": (within_type_norm, within_type_mixed),
    }


def print_grouped_view(weights_by_length):
    print(f"\n{'=' * 78}")
    print("Grouped read-out of the SAME flat pairwise-LR fit (no new fitting --")
    print("coefficients regrouped + normalized within each group for readability)")
    print("=" * 78)
    for l in LENGTHS:
        if l not in weights_by_length:
            continue
        gv = grouped_view(weights_by_length[l])
        top_norm, top_mixed = gv["top"]
        fd_norm, fd_mixed = gv["fd"]
        type_norm, type_mixed = gv["typemix"]
        within_norm, within_mixed = gv["within_type"]

        print(f"\n--- L{l} ---")

        def line(label, norm, mixed):
            flag = "  [MIXED SIGN -- share reading unreliable]" if mixed else ""
            parts = "  ".join(f"{k}={v:.3f}" for k, v in norm.items())
            print(f"  {label:<10}{parts}{flag}")

        line("top", top_norm, top_mixed)
        line("fd", fd_norm, fd_mixed)
        line("typemix", type_norm, type_mixed)
        for name in WITHIN_TYPE_GROUPS:
            if len(WITHIN_TYPE_GROUPS[name]) > 1:
                line(name, within_norm[name], within_mixed[name])


def eval_selector(selector, groups, keys):
    """Acc over the given case keys: fraction where the argmax script is
    correct. selector is either a weight vector (dotted with r['_x']) or the
    string '_baseline' (argmax on the CSV's own precomputed column)."""
    n_total = n_correct = 0
    for key in keys:
        rows = groups.get(key)
        if not rows:
            continue
        if isinstance(selector, str):
            best = max(rows, key=lambda r: r[selector])
        else:
            best = max(rows, key=lambda r: float(np.dot(selector, r["_x"])))
        n_total += 1
        n_correct += best["_y"] == 1
    return n_correct, n_total


def missed_cases(selector, groups, keys):
    """Among cases in `keys`, split into: no correct script generated at all
    (unfixable by any weighting), vs. >=1 correct script exists but the
    argmax pick under `selector` isn't one of them ("still not identified").
    Returns (n_has_correct, n_missed, n_no_correct_at_all)."""
    n_has_correct = n_missed = n_no_correct = 0
    for key in keys:
        rows = groups.get(key)
        if not rows:
            continue
        if not any(r["_y"] == 1 for r in rows):
            n_no_correct += 1
            continue
        n_has_correct += 1
        if isinstance(selector, str):
            best = max(rows, key=lambda r: r[selector])
        else:
            best = max(rows, key=lambda r: float(np.dot(selector, r["_x"])))
        if best["_y"] != 1:
            n_missed += 1
    return n_has_correct, n_missed, n_no_correct


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="scraped_scripts/scraped_scripts_scores.csv")
    args = parser.parse_args()

    rows = load_rows(args.csv)
    groups_all = group_by_case(rows)
    print(f"Loaded {len(rows)} usable rows across {len(groups_all)} cases")
    per_length_cases = {}
    for (length, _case) in groups_all:
        per_length_cases[length] = per_length_cases.get(length, 0) + 1
    print("Cases per length:", {l: per_length_cases.get(l, 0) for l in LENGTHS})

    weights_by_length = {}
    for held_out in LENGTHS:
        train_groups = {
            k: v for k, v in groups_all.items() if k[0] != held_out
        }
        test_keys = [k for k in groups_all if k[0] == held_out]

        w = fit_pairwise(train_groups)
        if w is None:
            print(f"\nL{held_out}: no pairwise training pairs available -- skipped")
            continue
        weights_by_length[held_out] = w

        n_correct, n_total = eval_selector(w, groups_all, test_keys)
        n_base_correct, n_base_total = eval_selector("_baseline", groups_all, test_keys)
        w_norm = w / np.sum(np.abs(w))

        print(f"\n{'=' * 78}")
        print(f"Held-out length {held_out}  (trained on lengths "
              f"{[l for l in LENGTHS if l != held_out]})")
        print("=" * 78)
        print(f"{'feature':<18}{'raw':>10}{'normalized':>14}")
        for f, v, vn in zip(LEAF_FEATURES, w, w_norm):
            print(f"{f:<18}{v:>10.4f}{vn:>14.4f}")
        if n_total:
            print(f"\nAccuracy on held-out L{held_out} cases: "
                  f"pairwise-LR {n_correct}/{n_total} ({100 * n_correct / n_total:.1f}%)"
                  f"  vs equal-weight score_1 baseline "
                  f"{n_base_correct}/{n_base_total} ({100 * n_base_correct / n_base_total:.1f}%)")

    print(f"\n{'=' * 78}")
    print(f"Summary: {len(weights_by_length)} weight vectors, one per held-out length")
    print("=" * 78)
    header = f"{'feature':<18}" + "".join(f"{'L' + l:<10}" for l in LENGTHS)
    print(header)
    for i, feat in enumerate(LEAF_FEATURES):
        line = f"{feat:<18}"
        for l in LENGTHS:
            line += f"{weights_by_length[l][i]:<10.4f}" if l in weights_by_length else f"{'--':<10}"
        print(line)

    # ── Still-not-identified breakdown: of the cases where a correct script
    # actually exists among the candidates, how many does each selector still
    # fail to surface? (cases with zero correct candidates are excluded here --
    # no weighting can ever fix those.) ─────────────────────────────────────
    print(f"\n{'=' * 78}")
    print("Correct-script-exists-but-not-selected, per length")
    print("=" * 78)
    print(f"{'length':<8}{'total':>7}{'no_correct_avail':>18}{'has_correct':>13}"
          f"{'missed(equal-wt)':>18}{'missed(weighted)':>18}")
    tot_total = tot_has = tot_no = tot_miss_base = tot_miss_w = 0
    for l in LENGTHS:
        test_keys = [k for k in groups_all if k[0] == l]
        n_has_b, n_missed_b, n_no_b = missed_cases("_baseline", groups_all, test_keys)
        if l in weights_by_length:
            n_has_w, n_missed_w, n_no_w = missed_cases(weights_by_length[l], groups_all, test_keys)
        else:
            n_has_w, n_missed_w, n_no_w = n_has_b, None, n_no_b
        print(f"L{l:<7}{len(test_keys):>7}{n_no_b:>18}{n_has_b:>13}"
              f"{n_missed_b:>18}{(n_missed_w if n_missed_w is not None else '--'):>18}")
        tot_total += len(test_keys)
        tot_has += n_has_b
        tot_no += n_no_b
        tot_miss_base += n_missed_b
        if n_missed_w is not None:
            tot_miss_w += n_missed_w
    print(f"{'TOTAL':<8}{tot_total:>7}{tot_no:>18}{tot_has:>13}{tot_miss_base:>18}{tot_miss_w:>18}")
    print(f"\n({tot_no} cases have no correct script among any candidate at all -- "
          f"unfixable by any weighting. Of the remaining {tot_has} cases that DO have a "
          f"correct candidate, equal-weight score_1 still fails to surface it in "
          f"{tot_miss_base}, vs {tot_miss_w} for the per-length leave-one-out weighted model.)")

    print_grouped_view(weights_by_length)


if __name__ == "__main__":
    main()
