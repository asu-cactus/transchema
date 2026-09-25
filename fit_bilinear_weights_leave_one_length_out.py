"""
fit_bilinear_weights_leave_one_length_out.py
================================================
Trains the nested score formalization directly via MULTIPLICATION of its
component weights (confirmed structure: top x type x signal), rather than
either (a) fitting one independent flat coefficient per leaf feature
(fit_weights_leave_one_length_out.py) or (b) softmax-simplex-constraining
each group to sum to 1 (fit_grouped_weights_leave_one_length_out.py -- the
attempt that collapsed without heavy regularization).

    score        = w_fd*fd_f1 + w_col*ColumnScore
                 + w_row*row_count_score + w_miss*max_missing_score
    ColumnScore  = (n_float*avg_float + n_int*avg_int + n_id*avg_id
                    + n_cat*avg_cat + n_date*avg_date_score) / n_total_cols
    avg_float    = w_float_js*avg_float_js + w_float_range*avg_float_range
    avg_int      = w_int_js*avg_int_js + w_int_range*avg_int_range
                 + w_int_nunique*avg_int_nunique + w_int_missing*avg_int_missing
    avg_id       = w_id_nunique*avg_id_nunique + w_id_missing*avg_id_missing
    avg_cat      = w_cat_prop*avg_cat_prop + w_cat_nunique*avg_cat_nunique
                 + w_cat_missing*avg_cat_missing

IMPORTANT: ColumnScore has NO per-type weight (no w_float/w_int/w_id/w_cat/
w_date). Column TYPES are not weighted against each other -- individual
COLUMNS are averaged directly, via a genuine column-count-weighted mean
(n_float, n_int, ... are each case's actual GT column counts per type,
fixed by the ground-truth schema). An earlier version of this model gave
each type its own free weight (w_type_float * avg_float + ...), which meant
a type with only 1 column (e.g. date) got the same "importance slot" as a
type with 10 columns (e.g. int) -- a candidate that nailed 9/10 int columns
but missed its 1 date column could lose to one that only got 5/10 int
columns right but nailed the date column, because the type-level weight had
no notion of how many actual columns each type represented. Averaging over
individual columns (weighted by how many columns each type actually has)
fixes that: a type's influence on ColumnScore is now proportional to its
share of the table's columns, with no separate importance weight needed.

fd_f1 is used directly here (NOT split into precision/recall) -- production's
actual harmonic-mean formula, per instruction. Every within-type leaf
feature's effective coefficient is a product of 2 free scalars (e.g.
avg_int_js's is w_col*w_int_js, scaled by that case's n_int/n_total_cols
ratio) -- nonlinear/non-convex in the trainable parameters, unlike the flat
fit's one-coefficient-per-feature linear model, but with one less
multiplicative level than the type-weighted version had.

No softmax/simplex constraint this time -- weights are free, unconstrained
reals. Missing-type handling needs no masking trick either: a script with
zero columns of a given type already has that type's raw features imputed to
0 in the CSV, so w_type * 0 = 0 regardless of w_type's value.

Regularization: L2 weight decay (via Adam's weight_decay) discourages the
classic bilinear-model failure mode (one factor blowing up while another
shrinks to compensate, keeping the product's training loss stable while the
individual weights drift to meaningless magnitudes). Same early-stopping
discipline as the softmax attempt: fit on an inner 85% of the training pool's
own cases, model-select on missed-cases over the inner 15%, not on the
training loss itself.

Same leave-one-length-out evaluation as the other two fits: for each length
L, train on every OTHER length's (case, script) pairs, evaluate only on L.

Usage: python3 fit_bilinear_weights_leave_one_length_out.py [--csv PATH] [--epochs N] [--lr LR] [--weight_decay WD]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import argparse
import csv
import random as _random

import numpy as np
import torch

LENGTHS = ["1", "2", "3", "4", "5", "9"]

RAW_COLS = [
    "fd_f1",
    "avg_float_js", "avg_float_range",
    "avg_int_js", "avg_int_range", "avg_int_nunique", "avg_int_missing",
    "avg_id_nunique", "avg_id_missing",
    "avg_cat_prop", "avg_cat_nunique", "avg_cat_missing",
    "avg_date_score",
    "row_count_score", "max_missing_score",
    # column-type COUNTS -- ColumnScore is a genuine column-count-weighted
    # average across every individual GT column, not a per-type weight (see
    # module docstring). These ride through the same X tensor as everything
    # else purely for convenience.
    "n_float_cols", "n_int_cols", "n_id_cols", "n_cat_cols", "n_date_cols",
]
IDX = {name: i for i, name in enumerate(RAW_COLS)}
BASELINE_COL = "score_1"


def _float_or(v, default=0.0):
    return float(v) if v not in ("", None) else default


def load_rows(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    usable = [r for r in rows if r.get("fd_f1", "") != "" and r.get("is_match") in ("True", "False")]
    for r in usable:
        r["_raw"] = np.array([_float_or(r[k]) for k in RAW_COLS], dtype=np.float32)
        r["_y"] = 1 if r["is_match"] == "True" else 0
        r["_baseline"] = _float_or(r.get(BASELINE_COL))
    return usable


def group_by_case(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r["length"], r["case_num"]), []).append(r)
    return groups


# ---------------------------------------------------------------------------
# Bilinear scorer -- every group weight is a free scalar, no simplex constraint
# ---------------------------------------------------------------------------

PARAM_SPEC = {
    # name -> number of scalars in that group
    "top": 4,        # fd, col, row, miss
    "float": 2,       # js, range
    "int": 4,         # js, range, nunique, missing
    "id": 2,          # nunique, missing
    "cat": 3,         # prop, nunique, missing
}


class BilinearScorer:
    """Every weight GROUP (top, float, int, id, cat) is a free, unconstrained
    real-valued vector -- trained via Adam + L2 weight_decay + early
    stopping, no simplex constraint baked into training (that version
    trained less reliably -- see the softmax attempt this replaced). The
    column-type combination is a column-COUNT-weighted average (n_float/
    n_total + n_int/n_total + ... already sums to 1 for free, from the data,
    no learned type weight needed)."""

    def __init__(self, seed=0):
        g = torch.Generator().manual_seed(seed)

        def init(n):
            # start near 1.0 (not near 0) so PRODUCTS start at a sensible
            # O(1) scale instead of vanishing -- a product of near-zero
            # random inits would give a near-zero score with a near-zero
            # gradient almost everywhere.
            return torch.nn.Parameter(1.0 + 0.05 * torch.randn(n, generator=g))

        self.w_top = init(PARAM_SPEC["top"])       # fd, col, row, miss
        self.w_float = init(PARAM_SPEC["float"])
        self.w_int = init(PARAM_SPEC["int"])
        self.w_id = init(PARAM_SPEC["id"])
        self.w_cat = init(PARAM_SPEC["cat"])

    def parameters(self):
        return [self.w_top, self.w_float, self.w_int, self.w_id, self.w_cat]

    def score(self, X):
        """X: (N, len(RAW_COLS)) float tensor. Returns (N,) score tensor (unbounded)."""
        avg_float = (self.w_float[0] * X[:, IDX["avg_float_js"]]
                     + self.w_float[1] * X[:, IDX["avg_float_range"]])
        avg_int = (self.w_int[0] * X[:, IDX["avg_int_js"]] + self.w_int[1] * X[:, IDX["avg_int_range"]]
                   + self.w_int[2] * X[:, IDX["avg_int_nunique"]] + self.w_int[3] * X[:, IDX["avg_int_missing"]])
        avg_id = self.w_id[0] * X[:, IDX["avg_id_nunique"]] + self.w_id[1] * X[:, IDX["avg_id_missing"]]
        avg_cat = (self.w_cat[0] * X[:, IDX["avg_cat_prop"]] + self.w_cat[1] * X[:, IDX["avg_cat_nunique"]]
                   + self.w_cat[2] * X[:, IDX["avg_cat_missing"]])
        avg_date = X[:, IDX["avg_date_score"]]

        n_float = X[:, IDX["n_float_cols"]]
        n_int = X[:, IDX["n_int_cols"]]
        n_id = X[:, IDX["n_id_cols"]]
        n_cat = X[:, IDX["n_cat_cols"]]
        n_date = X[:, IDX["n_date_cols"]]
        n_total = n_float + n_int + n_id + n_cat + n_date

        # Column-COUNT-weighted average across every individual GT column --
        # NOT a per-type weight (see module docstring for why that was a bug).
        column_score = (n_float * avg_float + n_int * avg_int + n_id * avg_id
                        + n_cat * avg_cat + n_date * avg_date) / (n_total + 1e-9)

        return (self.w_top[0] * X[:, IDX["fd_f1"]] + self.w_top[1] * column_score
                + self.w_top[2] * X[:, IDX["row_count_score"]] + self.w_top[3] * X[:, IDX["max_missing_score"]])

    def resolved_weights(self):
        with torch.no_grad():
            return {
                "top [fd, col, row, miss]": self.w_top.tolist(),
                "float [js, range]": self.w_float.tolist(),
                "int [js, range, nunique, missing]": self.w_int.tolist(),
                "id [nunique, missing]": self.w_id.tolist(),
                "cat [prop, nunique, missing]": self.w_cat.tolist(),
            }

    def resolved_weights_normalized(self):
        """Post-hoc: normalize each group's raw weights to sum to 1 (for a
        readable, [0,1]-flavored REPORT only). NOTE: unlike the flat fit's
        grouped view, this is NOT guaranteed to preserve the same argmax
        decisions as the raw weights -- see the "Are they being normalized"
        discussion. Use resolved_weights() (raw) for the actual scores this
        model was fit and evaluated with; use this only for a human-readable
        summary, and check missed-cases under it separately before trusting
        it as a replacement scorer."""
        raw = self.resolved_weights()
        norm = {}
        for name, vals in raw.items():
            total = sum(vals)
            mixed = any(v < 0 for v in vals) and any(v > 0 for v in vals)
            if abs(total) < 1e-9:
                norm[name] = ([float("nan")] * len(vals), mixed)
            else:
                norm[name] = ([v / total for v in vals], mixed)
        return norm

    def effective_leaf_coefficients(self, counts=None):
        """The actual per-leaf-feature multipliers this scorer reduces to.

        Since ColumnScore is now a column-COUNT-weighted average (not a
        per-type weight), each leaf's effective coefficient depends on that
        specific case's column composition -- pass counts as a dict
        {"n_float_cols": .., "n_int_cols": .., ...} for a case-specific
        readout. Without it, only the within-type signal shares are
        returned (how much JS matters vs range within int, etc.) -- the
        cross-type mixing can't be reduced to one constant anymore."""
        w = self.resolved_weights()
        top_fd, top_col, top_row, top_miss = w["top [fd, col, row, miss]"]
        f_js, f_range = w["float [js, range]"]
        i_js, i_range, i_nunique, i_missing = w["int [js, range, nunique, missing]"]
        id_nunique, id_missing = w["id [nunique, missing]"]
        c_prop, c_nunique, c_missing = w["cat [prop, nunique, missing]"]

        base = {"fd_f1": top_fd, "row_count_score": top_row, "max_missing_score": top_miss}
        if counts is None:
            base.update({
                "avg_float_js": f_js, "avg_float_range": f_range,
                "avg_int_js": i_js, "avg_int_range": i_range,
                "avg_int_nunique": i_nunique, "avg_int_missing": i_missing,
                "avg_id_nunique": id_nunique, "avg_id_missing": id_missing,
                "avg_cat_prop": c_prop, "avg_cat_nunique": c_nunique, "avg_cat_missing": c_missing,
                "avg_date_score": None,
            })
            return base

        n_total = sum(counts.values()) + 1e-9
        share_float = top_col * counts["n_float_cols"] / n_total
        share_int = top_col * counts["n_int_cols"] / n_total
        share_id = top_col * counts["n_id_cols"] / n_total
        share_cat = top_col * counts["n_cat_cols"] / n_total
        share_date = top_col * counts["n_date_cols"] / n_total
        base.update({
            "avg_float_js": share_float * f_js, "avg_float_range": share_float * f_range,
            "avg_int_js": share_int * i_js, "avg_int_range": share_int * i_range,
            "avg_int_nunique": share_int * i_nunique, "avg_int_missing": share_int * i_missing,
            "avg_id_nunique": share_id * id_nunique, "avg_id_missing": share_id * id_missing,
            "avg_cat_prop": share_cat * c_prop, "avg_cat_nunique": share_cat * c_nunique,
            "avg_cat_missing": share_cat * c_missing,
            "avg_date_score": share_date,
        })
        return base


# ---------------------------------------------------------------------------
# Fitting
# ---------------------------------------------------------------------------

def _score_rows(scorer, rows):
    X = torch.tensor(np.stack([r["_raw"] for r in rows]))
    with torch.no_grad():
        return scorer.score(X)


def missed_cases_scorer(scorer, groups, keys):
    n_has = n_missed = n_no = 0
    for key in keys:
        rows = groups.get(key)
        if not rows:
            continue
        if not any(r["_y"] == 1 for r in rows):
            n_no += 1
            continue
        n_has += 1
        best_idx = int(torch.argmax(_score_rows(scorer, rows)).item())
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


def eval_scorer(scorer, groups, keys):
    n_total = n_correct = 0
    for key in keys:
        rows = groups.get(key)
        if not rows:
            continue
        best_idx = int(torch.argmax(_score_rows(scorer, rows)).item())
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


def fit_bilinear(train_groups, epochs=3000, lr=0.02, seed=0,
                  weight_decay=0.01, val_frac=0.15, patience=15, eval_every=25):
    case_keys = sorted(train_groups.keys())
    rng = _random.Random(seed)
    shuffled = case_keys[:]
    rng.shuffle(shuffled)
    n_val = max(1, int(len(shuffled) * val_frac))
    val_keys = shuffled[:n_val]
    inner_train_keys = set(shuffled[n_val:])
    inner_train_groups = {k: v for k, v in train_groups.items() if k in inner_train_keys}

    all_rows = []
    row_of = {}
    for rows in inner_train_groups.values():
        for r in rows:
            row_of[id(r)] = len(all_rows)
            all_rows.append(r)
    if not all_rows:
        return None, None

    pos_idx, neg_idx = [], []
    for rows in inner_train_groups.values():
        pos = [row_of[id(r)] for r in rows if r["_y"] == 1]
        neg = [row_of[id(r)] for r in rows if r["_y"] == 0]
        for p in pos:
            for n in neg:
                pos_idx.append(p)
                neg_idx.append(n)
    if not pos_idx:
        return None, None

    X = torch.tensor(np.stack([r["_raw"] for r in all_rows]))
    pos_idx = torch.tensor(pos_idx, dtype=torch.long)
    neg_idx = torch.tensor(neg_idx, dtype=torch.long)

    scorer = BilinearScorer(seed=seed)
    opt = torch.optim.Adam(scorer.parameters(), lr=lr, weight_decay=weight_decay)
    param_names = ["w_top", "w_float", "w_int", "w_id", "w_cat"]

    best_missed = None
    best_state = None
    epochs_since_improve = 0
    loss_val = None

    for epoch in range(epochs):
        opt.zero_grad()
        scores = scorer.score(X)
        margin = scores[pos_idx] - scores[neg_idx]
        loss = torch.nn.functional.softplus(-margin).mean()
        loss.backward()
        opt.step()
        loss_val = float(loss.item())

        if epoch % eval_every == 0 or epoch == epochs - 1:
            _, n_missed, _ = missed_cases_scorer(scorer, train_groups, val_keys)
            if best_missed is None or n_missed < best_missed:
                best_missed = n_missed
                best_state = {name: getattr(scorer, name).detach().clone() for name in param_names}
                epochs_since_improve = 0
            else:
                epochs_since_improve += 1
            if epochs_since_improve >= patience:
                break

    if best_state is not None:
        with torch.no_grad():
            for name in param_names:
                getattr(scorer, name).data.copy_(best_state[name])

    return scorer, loss_val


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="scraped_scripts/scraped_scripts_scores.csv")
    parser.add_argument("--epochs", type=int, default=3000)
    parser.add_argument("--lr", type=float, default=0.02)
    parser.add_argument("--weight_decay", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--val_frac", type=float, default=0.15)
    parser.add_argument("--patience", type=int, default=15)
    parser.add_argument("--eval_every", type=int, default=25)
    args = parser.parse_args()

    rows = load_rows(args.csv)
    groups_all = group_by_case(rows)
    print(f"Loaded {len(rows)} usable rows across {len(groups_all)} cases")
    per_length_cases = {}
    for (length, _case) in groups_all:
        per_length_cases[length] = per_length_cases.get(length, 0) + 1
    print("Cases per length:", {l: per_length_cases.get(l, 0) for l in LENGTHS})

    tot_has = tot_no = tot_miss_base = tot_miss_grp = 0
    for held_out in LENGTHS:
        train_groups = {k: v for k, v in groups_all.items() if k[0] != held_out}
        test_keys = [k for k in groups_all if k[0] == held_out]

        scorer, final_loss = fit_bilinear(
            train_groups, epochs=args.epochs, lr=args.lr, seed=args.seed,
            weight_decay=args.weight_decay, val_frac=args.val_frac,
            patience=args.patience, eval_every=args.eval_every,
        )
        if scorer is None:
            print(f"\nL{held_out}: no pairwise training pairs available -- skipped")
            continue

        n_correct, n_total = eval_scorer(scorer, groups_all, test_keys)
        n_base_correct, n_base_total = eval_baseline(groups_all, test_keys)
        n_has, n_missed, n_no = missed_cases_scorer(scorer, groups_all, test_keys)
        n_has_b, n_missed_b, n_no_b = missed_cases_baseline(groups_all, test_keys)

        print(f"\n{'=' * 78}")
        print(f"Held-out length {held_out}  (trained on lengths "
              f"{[l for l in LENGTHS if l != held_out]}, final train loss={final_loss:.4f})")
        print("=" * 78)
        for name, vals in scorer.resolved_weights().items():
            print(f"  {name:<38}" + "  ".join(f"{v:+.4f}" for v in vals))
        print("  effective leaf coefficients (within-type shares; cross-type mixing is")
        print("  now column-count-weighted per case, not a fixed constant -- see docstring):")
        for k, v in scorer.effective_leaf_coefficients().items():
            print(f"    {k:<20}" + (f"{v:+.4f}" if v is not None else "(depends on case's column counts)"))

        if n_total:
            print(f"\nAccuracy on held-out L{held_out} cases: "
                  f"bilinear {n_correct}/{n_total} ({100 * n_correct / n_total:.1f}%)"
                  f"  vs equal-weight score_1 baseline "
                  f"{n_base_correct}/{n_base_total} ({100 * n_base_correct / n_base_total:.1f}%)")
        print(f"Missed (correct exists, not selected): bilinear {n_missed}/{n_has}"
              f"  vs equal-weight {n_missed_b}/{n_has_b}  (no_correct_avail={n_no})")

        tot_has += n_has
        tot_no += n_no
        tot_miss_base += n_missed_b
        tot_miss_grp += n_missed

    print(f"\n{'=' * 78}")
    print("TOTAL across all held-out lengths")
    print("=" * 78)
    print(f"no_correct_avail (unfixable): {tot_no}")
    print(f"has_correct: {tot_has}")
    print(f"missed -- equal-weight baseline: {tot_miss_base}")
    print(f"missed -- bilinear (product) model: {tot_miss_grp}")


if __name__ == "__main__":
    main()
