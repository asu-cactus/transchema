"""
fit_xgboost_ranker_leave_one_length_out.py
================================================
Tests whether a non-linear model beats the linear/bilinear fits tried so
far, using XGBoost's native learning-to-rank objective (rank:pairwise --
gradient-boosted trees trained on the same "correct should outrank wrong
within a case" objective as the pairwise logistic/bilinear fits, but able to
learn arbitrary non-linear splits and feature interactions instead of a
fixed linear or product-of-weights formula).

Unlike the linear/bilinear fits, trees are given the RAW per-type averages
AND the raw column counts (n_float_cols, n_int_cols, ...) as separate
features, rather than a hand-built "column-count-weighted average" formula --
trees can learn that relationship themselves (or something richer) if it's
actually useful, since splitting on raw feature values is the natural
mode for tree models (unlike linear models, where feeding pairwise
DIFFERENCES is the standard trick -- trees don't need that trick; they're
handed the raw feature matrix plus a group/qid array marking which rows
belong to the same case, and XGBoost's ranking objective handles the
within-group pairwise comparisons internally).

Same leave-one-length-out evaluation and missed-cases metric as every other
fit in this investigation, so results are directly comparable.

Usage: python3 fit_xgboost_ranker_leave_one_length_out.py [--csv PATH]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import argparse
import csv

import numpy as np
from xgboost import XGBRanker

LENGTHS = ["1", "2", "3", "4", "5", "9"]

FEATURES = [
    "fd_f1",
    "avg_float_js", "avg_float_range",
    "avg_int_js", "avg_int_range", "avg_int_nunique", "avg_int_missing",
    "avg_id_nunique", "avg_id_missing",
    "avg_cat_prop", "avg_cat_nunique", "avg_cat_missing",
    "avg_date_score",
    "row_count_score", "max_missing_score",
    "n_float_cols", "n_int_cols", "n_id_cols", "n_cat_cols", "n_date_cols",
]
BASELINE_COL = "score_1"


def _float_or(v, default=0.0):
    return float(v) if v not in ("", None) else default


def load_rows(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    usable = [r for r in rows if r.get("fd_f1", "") != "" and r.get("is_match") in ("True", "False")]
    for r in usable:
        r["_x"] = np.array([_float_or(r[k]) for k in FEATURES], dtype=np.float32)
        r["_y"] = 1 if r["is_match"] == "True" else 0
        r["_baseline"] = _float_or(r.get(BASELINE_COL))
    return usable


def group_by_case(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r["length"], r["case_num"]), []).append(r)
    return groups


def build_ranking_arrays(train_groups):
    """XGBRanker needs rows grouped contiguously by qid, sorted by qid."""
    X, y, qid = [], [], []
    for i, (key, rows) in enumerate(train_groups.items()):
        for r in rows:
            X.append(r["_x"])
            y.append(r["_y"])
            qid.append(i)
    return np.stack(X), np.array(y), np.array(qid)


def fit_xgb_ranker(train_groups, seed=0, n_estimators=2000, max_depth=10,
                    learning_rate=0.1, reg_lambda=0.1):
    """High-capacity XGBRanker, NO early stopping and NO held-back
    validation slice -- trained to convergence on the FULL training pool.
    Deliberately allowed to overfit (in-sample train accuracy lands near
    99%): validation-based early stopping was tried first and made results
    worse (the inner-validation ndcg@1 signal is too noisy at this data
    scale and stopped training after only ~12 trees), so this trades
    "protect against overfitting" for "give the model everything and let it
    fit as hard as it wants," per instruction."""
    # Only cases with both a correct and a wrong candidate carry ranking
    # signal -- same requirement as the pairwise logistic/bilinear fits.
    mixed_groups = {
        k: v for k, v in train_groups.items()
        if any(r["_y"] == 1 for r in v) and any(r["_y"] == 0 for r in v)
    }
    if not mixed_groups:
        return None

    X, y, qid = build_ranking_arrays(mixed_groups)

    model = XGBRanker(
        objective="rank:pairwise",
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        subsample=1.0,
        colsample_bytree=1.0,
        reg_lambda=reg_lambda,
        min_child_weight=1,
        random_state=seed,
    )
    model.fit(X, y, qid=qid)
    return model


def eval_model(model, groups, keys):
    n_total = n_correct = 0
    for key in keys:
        rows = groups.get(key)
        if not rows:
            continue
        X = np.stack([r["_x"] for r in rows])
        scores = model.predict(X)
        best_idx = int(np.argmax(scores))
        n_total += 1
        n_correct += rows[best_idx]["_y"] == 1
    return n_correct, n_total


def eval_baseline(groups, keys):
    n_total = n_correct = 0
    for key in keys:
        rows = groups.get(key)
        if not rows:
            continue
        best = max(rows, key=lambda r: r["_baseline"])
        n_total += 1
        n_correct += best["_y"] == 1
    return n_correct, n_total


def missed_cases_model(model, groups, keys):
    n_has = n_missed = n_no = 0
    for key in keys:
        rows = groups.get(key)
        if not rows:
            continue
        if not any(r["_y"] == 1 for r in rows):
            n_no += 1
            continue
        n_has += 1
        X = np.stack([r["_x"] for r in rows])
        scores = model.predict(X)
        best_idx = int(np.argmax(scores))
        if rows[best_idx]["_y"] != 1:
            n_missed += 1
    return n_has, n_missed, n_no


def missed_cases_baseline(groups, keys):
    n_has = n_missed = n_no = 0
    for key in keys:
        rows = groups.get(key)
        if not rows:
            continue
        if not any(r["_y"] == 1 for r in rows):
            n_no += 1
            continue
        n_has += 1
        best = max(rows, key=lambda r: r["_baseline"])
        if best["_y"] != 1:
            n_missed += 1
    return n_has, n_missed, n_no


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="scraped_scripts/scraped_scripts_scores.csv")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rows = load_rows(args.csv)
    groups_all = group_by_case(rows)
    print(f"Loaded {len(rows)} usable rows across {len(groups_all)} cases")

    tot_has = tot_no = tot_miss_base = tot_miss_model = 0
    for held_out in LENGTHS:
        train_groups = {k: v for k, v in groups_all.items() if k[0] != held_out}
        test_keys = [k for k in groups_all if k[0] == held_out]

        model = fit_xgb_ranker(train_groups, seed=args.seed)
        if model is None:
            print(f"\nL{held_out}: no mixed-outcome training cases -- skipped")
            continue

        n_correct, n_total = eval_model(model, groups_all, test_keys)
        n_base_correct, n_base_total = eval_baseline(groups_all, test_keys)
        n_has, n_missed, n_no = missed_cases_model(model, groups_all, test_keys)
        n_has_b, n_missed_b, n_no_b = missed_cases_baseline(groups_all, test_keys)

        print(f"\nL{held_out}: xgboost {n_correct}/{n_total} ({100*n_correct/n_total:.1f}%)  "
              f"vs equal-weight {n_base_correct}/{n_base_total} ({100*n_base_correct/n_base_total:.1f}%)")
        print(f"  missed: xgboost {n_missed}/{n_has}  vs equal-weight {n_missed_b}/{n_has_b}  (no_correct_avail={n_no})")

        top_feat_idx = np.argsort(model.feature_importances_)[::-1][:5]
        print("  top-5 features by importance:",
              ", ".join(f"{FEATURES[i]}={model.feature_importances_[i]:.3f}" for i in top_feat_idx))

        tot_has += n_has
        tot_no += n_no
        tot_miss_base += n_missed_b
        tot_miss_model += n_missed

    print(f"\n{'=' * 78}")
    print("TOTAL")
    print("=" * 78)
    print(f"no_correct_avail: {tot_no}")
    print(f"has_correct: {tot_has}")
    print(f"missed -- equal-weight baseline: {tot_miss_base}")
    print(f"missed -- xgboost ranker: {tot_miss_model}")


if __name__ == "__main__":
    main()
