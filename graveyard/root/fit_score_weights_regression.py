"""
fit_score_weights_regression.py
==================================
Fits weights for the 4 score_1 components (fd_f1, avg_col_score_1,
row_count_score, max_missing_score) against score_regression_dataset.csv,
using two regression formulations:

  A. Pointwise logistic regression: P(y=1|x) = sigmoid(w.x), treating each
     script as an i.i.d. sample. Simple baseline.
  B. Pairwise ranking regression: for every case with >=1 correct and >=1
     incorrect script, form all (positive, negative) pairs, fit logistic
     regression (no intercept) on the feature DIFFERENCE z = x_pos - x_neg
     with target=1 (w.z > 0). Directly optimizes "correct outranks incorrect
     within the same case", the actual selection objective.

Evaluation (the TRUE objective, not regression loss): for a held-out set of
CASES (not rows -- scripts from the same case are correlated), compute
  Acc(w) = fraction of cases where argmax_s w.x(s) has is_match=True
for: equal-weight baseline (current formula), pointwise-LR weights,
pairwise-LR weights. Split is by case (80/20), stratified by length, fixed
seed for reproducibility.

Usage: python3 fit_score_weights_regression.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import csv
import random
import numpy as np
from sklearn.linear_model import LogisticRegression

FEATURES = ["fd_f1", "avg_col_score_1", "row_count_score", "max_missing_score"]
SEED = 42


def load_clean_rows(path="score_regression_dataset.csv"):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    usable = [r for r in rows if r["train_run_ok"] == "True" and r["is_match"] in ("True", "False")]
    clean = [r for r in usable if all(r[k] != "" for k in FEATURES)]
    for r in clean:
        r["_x"] = np.array([float(r[k]) for k in FEATURES])
        r["_y"] = 1 if r["is_match"] == "True" else 0
    return clean


def split_cases(rows, test_frac=0.2, seed=SEED):
    """Split (length, case_num) keys 80/20, stratified by length."""
    by_length = {}
    for r in rows:
        by_length.setdefault(r["length"], set()).add(r["case_num"])

    rng = random.Random(seed)
    train_keys, test_keys = set(), set()
    for length, cases in by_length.items():
        cases = sorted(cases)
        rng.shuffle(cases)
        n_test = max(1, int(len(cases) * test_frac))
        test_cases = set(cases[:n_test])
        for c in cases:
            key = (length, c)
            if c in test_cases:
                test_keys.add(key)
            else:
                train_keys.add(key)
    return train_keys, test_keys


def group_by_case(rows):
    groups = {}
    for r in rows:
        key = (r["length"], r["case_num"])
        groups.setdefault(key, []).append(r)
    return groups


def fit_pointwise(train_rows):
    X = np.stack([r["_x"] for r in train_rows])
    y = np.array([r["_y"] for r in train_rows])
    clf = LogisticRegression(fit_intercept=True, max_iter=2000)
    clf.fit(X, y)
    return clf.coef_[0]


def fit_pairwise(train_groups):
    diffs = []
    for key, rows in train_groups.items():
        pos = [r for r in rows if r["_y"] == 1]
        neg = [r for r in rows if r["_y"] == 0]
        for p in pos:
            for n in neg:
                diffs.append(p["_x"] - n["_x"])
                diffs.append(n["_x"] - p["_x"])  # symmetric negative example
    Z = np.stack([d for d in diffs])
    # label: first half (pos-neg) -> 1, second half (neg-pos) -> 0
    y = np.array([1, 0] * (len(diffs) // 2))
    clf = LogisticRegression(fit_intercept=False, max_iter=2000)
    clf.fit(Z, y)
    return clf.coef_[0]


def eval_weights(w, groups, keys):
    """Acc(w) over the given case keys: fraction where argmax script is correct."""
    n_total = 0
    n_correct = 0
    per_length = {}
    for key in keys:
        rows = groups.get(key)
        if not rows:
            continue
        length = key[0]
        best = max(rows, key=lambda r: float(np.dot(w, r["_x"])))
        n_total += 1
        ok = best["_y"] == 1
        n_correct += ok
        pl = per_length.setdefault(length, [0, 0])
        pl[1] += 1
        pl[0] += ok
    return n_correct, n_total, per_length


def main():
    rows = load_clean_rows()
    print(f"Loaded {len(rows)} clean rows across "
          f"{len(set((r['length'], r['case_num']) for r in rows))} cases")

    train_keys, test_keys = split_cases(rows)
    print(f"Train cases: {len(train_keys)}, Test cases: {len(test_keys)}")

    train_rows = [r for r in rows if (r["length"], r["case_num"]) in train_keys]
    groups_all = group_by_case(rows)
    train_groups = {k: v for k, v in groups_all.items() if k in train_keys}

    equal_w = np.array([0.25, 0.25, 0.25, 0.25])
    pointwise_w = fit_pointwise(train_rows)
    pairwise_w = fit_pairwise(train_groups)

    def show(name, w):
        w_norm = w / np.sum(np.abs(w))
        print(f"\n{name} weights (raw): " + ", ".join(f"{f}={v:.4f}" for f, v in zip(FEATURES, w)))
        print(f"{name} weights (normalized, sum|w|=1): " + ", ".join(f"{f}={v:.4f}" for f, v in zip(FEATURES, w_norm)))

    show("Pointwise-LR", pointwise_w)
    show("Pairwise-LR", pairwise_w)

    print(f"\n{'='*70}\nEvaluation on HELD-OUT test cases ({len(test_keys)} cases)\n{'='*70}")
    for name, w in [("Equal-weight (current formula)", equal_w),
                    ("Pointwise-LR", pointwise_w),
                    ("Pairwise-LR", pairwise_w)]:
        n_correct, n_total, per_length = eval_weights(w, groups_all, test_keys)
        breakdown = "  ".join(f"L{l}={c}/{t}" for l, (c, t) in sorted(per_length.items()))
        print(f"{name:<32}: {n_correct}/{n_total} correct ({100*n_correct/n_total:.1f}%)   [{breakdown}]")

    print(f"\n{'='*70}\nEvaluation on TRAIN cases ({len(train_keys)} cases, in-sample, for reference)\n{'='*70}")
    for name, w in [("Equal-weight (current formula)", equal_w),
                    ("Pointwise-LR", pointwise_w),
                    ("Pairwise-LR", pairwise_w)]:
        n_correct, n_total, per_length = eval_weights(w, groups_all, train_keys)
        breakdown = "  ".join(f"L{l}={c}/{t}" for l, (c, t) in sorted(per_length.items()))
        print(f"{name:<32}: {n_correct}/{n_total} correct ({100*n_correct/n_total:.1f}%)   [{breakdown}]")


if __name__ == "__main__":
    main()
