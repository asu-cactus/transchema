"""
fit_score_weights_lp.py
==========================
LP formulation: find weights w=(w1,w2,w3,w4) on the 4 score_1 components
(fd_f1, avg_col_score_1, row_count_score, max_missing_score) that minimize
the total absolute gap between det_score_reward = w.x(s) (train-side,
mirrors MCTS reward) and partial_reward(s) (test-side, held-out fuzzy
correctness signal from compare_tables_fuzzy):

  minimize   sum_s e_s
  subject to e_s >= partial_reward(s) - w.x(s)     for every script s
             e_s >= w.x(s) - partial_reward(s)      for every script s
             sum_j w_j = 1
             w_j >= 0                               j=1..4
             e_s >= 0

Solved exactly via scipy.optimize.linprog (no approximation). Weights fit on
80% of cases (stratified by length), evaluated on the held-out 20% both by
LP objective (mean absolute gap) and by the downstream argmax-selection
accuracy metric used throughout this analysis.

Usage: python3 fit_score_weights_lp.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import csv
import random
import numpy as np
from scipy.optimize import linprog

FEATURES = ["fd_f1", "avg_col_score_1", "row_count_score", "max_missing_score"]
SEED = 42


def load_clean_rows(path="score_regression_dataset.csv"):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    usable = [r for r in rows if r["train_run_ok"] == "True"
              and r["test_run_ok"] == "True" and r["partial_reward"] != ""]
    clean = [r for r in usable if all(r[k] != "" for k in FEATURES)]
    for r in clean:
        r["_x"] = np.array([float(r[k]) for k in FEATURES])
        r["_pr"] = float(r["partial_reward"])
        r["_y"] = 1 if r["is_match"] == "True" else 0
    return clean


def split_cases(rows, test_frac=0.2, seed=SEED):
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
            (test_keys if c in test_cases else train_keys).add(key)
    return train_keys, test_keys


def group_by_case(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r["length"], r["case_num"]), []).append(r)
    return groups


def solve_lp(train_rows):
    """minimize sum(e) s.t. e >= pr - w.x, e >= w.x - pr, sum(w)=1, w>=0, e>=0."""
    n = len(train_rows)
    X = np.stack([r["_x"] for r in train_rows])   # (n, 4)
    pr = np.array([r["_pr"] for r in train_rows])  # (n,)

    # variables: [w1..w4, e1..en]
    n_vars = 4 + n
    c = np.concatenate([np.zeros(4), np.ones(n)])  # minimize sum(e)

    # e_s - w.x_s >= -pr_s   ->   -w.x_s - e_s <= -pr_s  (as <=)
    #   i.e.  X @ w - e <= pr   ... let's derive A_ub properly below.
    # Constraint 1: pr - w.x <= e   ->   -X@w - e <= -pr
    A1 = np.hstack([-X, -np.eye(n)])
    b1 = -pr
    # Constraint 2: w.x - pr <= e   ->   X@w - e <= pr
    A2 = np.hstack([X, -np.eye(n)])
    b2 = pr

    A_ub = np.vstack([A1, A2])
    b_ub = np.concatenate([b1, b2])

    A_eq = np.concatenate([np.ones(4), np.zeros(n)]).reshape(1, -1)
    b_eq = np.array([1.0])

    bounds = [(0, None)] * 4 + [(0, None)] * n  # w>=0, e>=0

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                   bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(f"LP failed: {res.message}")
    w = res.x[:4]
    mean_abs_gap = res.fun / n
    return w, mean_abs_gap


def eval_gap(w, rows):
    gaps = [abs(r["_pr"] - float(np.dot(w, r["_x"]))) for r in rows]
    return float(np.mean(gaps))


def eval_selection_acc(w, groups, keys):
    n_correct = n_total = 0
    per_length = {}
    for key in keys:
        rs = groups.get(key)
        if not rs:
            continue
        length = key[0]
        best = max(rs, key=lambda r: float(np.dot(w, r["_x"])))
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
    train_rows = [r for r in rows if (r["length"], r["case_num"]) in train_keys]
    test_rows = [r for r in rows if (r["length"], r["case_num"]) in test_keys]
    groups = group_by_case(rows)
    print(f"Train cases: {len(train_keys)} ({len(train_rows)} rows), "
          f"Test cases: {len(test_keys)} ({len(test_rows)} rows)")

    w_lp, train_mean_gap = solve_lp(train_rows)
    equal_w = np.array([0.25, 0.25, 0.25, 0.25])

    print(f"\nLP weights: " + ", ".join(f"{f}={v:.4f}" for f, v in zip(FEATURES, w_lp)))
    print(f"  (sums to {w_lp.sum():.4f} by construction)")

    print(f"\n{'='*70}\nMean absolute gap |partial_reward - det_score_reward|\n{'='*70}")
    for name, w in [("Equal-weight (current)", equal_w), ("LP-optimal", w_lp)]:
        train_gap = eval_gap(w, train_rows)
        test_gap = eval_gap(w, test_rows)
        print(f"{name:<26}: train={train_gap:.4f}   test={test_gap:.4f}")

    print(f"\n{'='*70}\nDownstream metric: argmax-selection accuracy (held-out {len(test_keys)} cases)\n{'='*70}")
    for name, w in [("Equal-weight (current)", equal_w), ("LP-optimal", w_lp)]:
        n_correct, n_total, per_length = eval_selection_acc(w, groups, test_keys)
        breakdown = "  ".join(f"L{l}={c}/{t}" for l, (c, t) in sorted(per_length.items()))
        print(f"{name:<26}: {n_correct}/{n_total} correct ({100*n_correct/n_total:.1f}%)   [{breakdown}]")

    print(f"\n{'='*70}\nDownstream metric: argmax-selection accuracy (ALL {len(train_keys)+len(test_keys)} cases)\n{'='*70}")
    all_keys = train_keys | test_keys
    for name, w in [("Equal-weight (current)", equal_w), ("LP-optimal", w_lp)]:
        n_correct, n_total, per_length = eval_selection_acc(w, groups, all_keys)
        breakdown = "  ".join(f"L{l}={c}/{t}" for l, (c, t) in sorted(per_length.items()))
        print(f"{name:<26}: {n_correct}/{n_total} correct ({100*n_correct/n_total:.1f}%)   [{breakdown}]")


if __name__ == "__main__":
    main()
