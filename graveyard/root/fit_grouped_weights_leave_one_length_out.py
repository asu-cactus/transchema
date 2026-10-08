"""
fit_grouped_weights_leave_one_length_out.py
================================================
Fits the NESTED/grouped weight structure (as opposed to the flat 16-leaf-
feature fit in fit_weights_leave_one_length_out.py):

    score        = w_fd*fd_score + w_col*ColumnScore
                 + w_row*row_count_score + w_miss*max_missing_score
    fd_score     = w_precision*precision + w_recall*recall
    ColumnScore  = sum_t w_type_t * avg_t        (t in float/int/id/cat/date,
                                                    renormalized per-script over
                                                    only the types actually
                                                    present in that script's
                                                    table)
    avg_float    = w_float_js*avg_float_js + w_float_range*avg_float_range
    avg_int      = w_int_js*avg_int_js + w_int_range*avg_int_range
                 + w_int_nunique*avg_int_nunique + w_int_missing*avg_int_missing
    avg_id       = w_id_nunique*avg_id_nunique + w_id_missing*avg_id_missing
    avg_cat      = w_cat_prop*avg_cat_prop + w_cat_nunique*avg_cat_nunique
                 + w_cat_missing*avg_cat_missing
    avg_date     = avg_date_score   (already a single pre-blended signal --
                                      the underlying scoring code doesn't
                                      expose separate js/range for dates)

Every group is a genuine probability simplex (non-negative, sums to 1) BY
CONSTRUCTION, via a softmax reparameterization of unconstrained real
parameters per group. Plain LogisticRegression (used in
fit_weights_leave_one_length_out.py) can't fit this: sklearn only ever
produces one free, unconstrained coefficient per raw feature, with no notion
of "these particular weights must sum to 1 together." Softmax turns each
group's constrained simplex-fitting problem into an unconstrained one, so
the WHOLE nested formula (including the per-script type-presence
renormalization, handled by masking absent types' logits to -inf before
softmax) can be optimized end-to-end with PyTorch autodiff against the same
pairwise ranking loss used for the flat fit.

Same leave-one-length-out evaluation as the flat fit: for each length L,
train on every OTHER length's (case, script) pairs, evaluate only on L's own
cases.

Usage: python3 fit_grouped_weights_leave_one_length_out.py [--csv PATH] [--epochs N] [--lr LR]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import argparse
import csv

import numpy as np
import torch
import torch.nn.functional as F

LENGTHS = ["1", "2", "3", "4", "5", "9"]

RAW_COLS = [
    "precision", "recall",
    "avg_float_js", "avg_float_range",
    "avg_int_js", "avg_int_range", "avg_int_nunique", "avg_int_missing",
    "avg_id_nunique", "avg_id_missing",
    "avg_cat_prop", "avg_cat_nunique", "avg_cat_missing",
    "avg_date_score",
    "row_count_score", "max_missing_score",
]
IDX = {name: i for i, name in enumerate(RAW_COLS)}
PRESENCE_COLS = ["n_float_cols", "n_int_cols", "n_id_cols", "n_cat_cols", "n_date_cols"]
BASELINE_COL = "score_1"
MASK_NEG = -1e9  # finite (not -inf) so an all-absent row still softmaxes to a valid uniform, never NaN


def _float_or(v, default=0.0):
    return float(v) if v not in ("", None) else default


def load_rows(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    usable = [r for r in rows if r.get("fd_f1", "") != "" and r.get("is_match") in ("True", "False")]
    for r in usable:
        r["_raw"] = np.array([_float_or(r[k]) for k in RAW_COLS], dtype=np.float32)
        r["_present"] = np.array([_float_or(r[k]) > 0 for k in PRESENCE_COLS], dtype=bool)
        r["_y"] = 1 if r["is_match"] == "True" else 0
        r["_baseline"] = _float_or(r.get(BASELINE_COL))
    return usable


def group_by_case(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r["length"], r["case_num"]), []).append(r)
    return groups


# ---------------------------------------------------------------------------
# Nested scorer
# ---------------------------------------------------------------------------

class GroupedScorer:
    """One softmax-reparameterized unconstrained theta vector per weight
    group; computes the nested score for a batch of rows."""

    def __init__(self, seed=0):
        g = torch.Generator().manual_seed(seed)

        def init(n):
            return torch.nn.Parameter(0.01 * torch.randn(n, generator=g))

        self.theta_top = init(4)      # fd, col, row, miss
        self.theta_fd = init(2)       # precision, recall
        self.theta_typemix = init(5)  # float, int, id, cat, date
        self.theta_float = init(2)    # js, range
        self.theta_int = init(4)      # js, range, nunique, missing
        self.theta_id = init(2)       # nunique, missing
        self.theta_cat = init(3)      # prop, nunique, missing

    def parameters(self):
        return [self.theta_top, self.theta_fd, self.theta_typemix,
                self.theta_float, self.theta_int, self.theta_id, self.theta_cat]

    def score(self, X, present):
        """X: (N, len(RAW_COLS)) float tensor.
        present: (N, 5) bool tensor -- float/int/id/cat/date column presence.
        Returns (N,) score tensor."""
        w_top = F.softmax(self.theta_top, dim=0)      # fd, col, row, miss
        w_fd = F.softmax(self.theta_fd, dim=0)         # precision, recall
        w_float = F.softmax(self.theta_float, dim=0)
        w_int = F.softmax(self.theta_int, dim=0)
        w_id = F.softmax(self.theta_id, dim=0)
        w_cat = F.softmax(self.theta_cat, dim=0)

        fd_score = w_fd[0] * X[:, IDX["precision"]] + w_fd[1] * X[:, IDX["recall"]]

        avg_float = w_float[0] * X[:, IDX["avg_float_js"]] + w_float[1] * X[:, IDX["avg_float_range"]]
        avg_int = (w_int[0] * X[:, IDX["avg_int_js"]] + w_int[1] * X[:, IDX["avg_int_range"]]
                   + w_int[2] * X[:, IDX["avg_int_nunique"]] + w_int[3] * X[:, IDX["avg_int_missing"]])
        avg_id = w_id[0] * X[:, IDX["avg_id_nunique"]] + w_id[1] * X[:, IDX["avg_id_missing"]]
        avg_cat = (w_cat[0] * X[:, IDX["avg_cat_prop"]] + w_cat[1] * X[:, IDX["avg_cat_nunique"]]
                   + w_cat[2] * X[:, IDX["avg_cat_missing"]])
        avg_date = X[:, IDX["avg_date_score"]]

        avg_stack = torch.stack([avg_float, avg_int, avg_id, avg_cat, avg_date], dim=1)  # (N,5)

        # Per-row type-mix softmax, renormalized over only the types present
        # in that row's table (absent types masked to a large-negative logit
        # -> ~0 weight after softmax, present types renormalize automatically).
        masked_logits = self.theta_typemix.unsqueeze(0).expand(X.shape[0], -1).clone()
        masked_logits = masked_logits.masked_fill(~present, MASK_NEG)
        w_typemix = F.softmax(masked_logits, dim=1)  # (N,5)

        column_score = (w_typemix * avg_stack).sum(dim=1)

        return (w_top[0] * fd_score + w_top[1] * column_score
                + w_top[2] * X[:, IDX["row_count_score"]] + w_top[3] * X[:, IDX["max_missing_score"]])

    def resolved_weights(self):
        """Softmax-resolved (interpretable, sum-to-1) weights per group."""
        with torch.no_grad():
            return {
                "top [fd, col, row, miss]": F.softmax(self.theta_top, dim=0).tolist(),
                "fd [precision, recall]": F.softmax(self.theta_fd, dim=0).tolist(),
                "typemix [float, int, id, cat, date]": F.softmax(self.theta_typemix, dim=0).tolist(),
                "float [js, range]": F.softmax(self.theta_float, dim=0).tolist(),
                "int [js, range, nunique, missing]": F.softmax(self.theta_int, dim=0).tolist(),
                "id [nunique, missing]": F.softmax(self.theta_id, dim=0).tolist(),
                "cat [prop, nunique, missing]": F.softmax(self.theta_cat, dim=0).tolist(),
            }


# ---------------------------------------------------------------------------
# Fitting
# ---------------------------------------------------------------------------

def _entropy_penalty(scorer):
    """-sum(entropy(group)) over the 6 non-per-row groups (typemix is
    regularized via its raw/unmasked softmax as a proxy -- the per-row masked
    version varies row to row, but discouraging the raw logits from
    sharpening achieves the same anti-collapse effect). Minimizing this term
    is equivalent to maximizing total entropy, i.e. discouraging any group
    from concentrating onto a single corner of its simplex."""
    penalty = 0.0
    for theta in (scorer.theta_top, scorer.theta_fd, scorer.theta_typemix,
                  scorer.theta_float, scorer.theta_int, scorer.theta_id, scorer.theta_cat):
        w = F.softmax(theta, dim=0)
        penalty = penalty - (w * torch.log(w + 1e-9)).sum()
    return penalty


def fit_grouped(train_groups, epochs=3000, lr=0.05, seed=0,
                 entropy_lambda=0.05, val_frac=0.15, patience=15, eval_every=25):
    """Fits on an INNER 85/15 (by default) split of train_groups' own cases --
    the pairwise loss (+ entropy regularization) is minimized on the inner
    85%, but model selection (which epoch's weights to keep) is driven by
    missed-cases on the inner 15%, i.e. the real argmax-correctness objective,
    not the surrogate loss. Early-stops once that validation metric hasn't
    improved for `patience` evaluations."""
    import random as _random

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
    present = torch.tensor(np.stack([r["_present"] for r in all_rows]))
    pos_idx = torch.tensor(pos_idx, dtype=torch.long)
    neg_idx = torch.tensor(neg_idx, dtype=torch.long)

    scorer = GroupedScorer(seed=seed)
    opt = torch.optim.Adam(scorer.parameters(), lr=lr)
    param_names = ["theta_top", "theta_fd", "theta_typemix", "theta_float",
                   "theta_int", "theta_id", "theta_cat"]

    best_missed = None
    best_state = None
    epochs_since_improve = 0
    loss_val = None

    for epoch in range(epochs):
        opt.zero_grad()
        scores = scorer.score(X, present)
        margin = scores[pos_idx] - scores[neg_idx]
        pairwise_loss = F.softplus(-margin).mean()
        loss = pairwise_loss + entropy_lambda * _entropy_penalty(scorer)
        loss.backward()
        opt.step()
        loss_val = float(pairwise_loss.item())

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
# Evaluation
# ---------------------------------------------------------------------------

def _score_rows(scorer, rows):
    X = torch.tensor(np.stack([r["_raw"] for r in rows]))
    present = torch.tensor(np.stack([r["_present"] for r in rows]))
    with torch.no_grad():
        return scorer.score(X, present)


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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="scraped_scripts/scraped_scripts_scores.csv")
    parser.add_argument("--epochs", type=int, default=3000)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--entropy_lambda", type=float, default=0.05,
                         help="Weight on the anti-collapse entropy penalty per softmax group")
    parser.add_argument("--val_frac", type=float, default=0.15,
                         help="Fraction of each training pool's own cases held out for early-stopping")
    parser.add_argument("--patience", type=int, default=15,
                         help="Early-stop after this many eval_every-spaced checks with no val improvement")
    parser.add_argument("--eval_every", type=int, default=25)
    args = parser.parse_args()

    torch.manual_seed(args.seed)

    rows = load_rows(args.csv)
    groups_all = group_by_case(rows)
    print(f"Loaded {len(rows)} usable rows across {len(groups_all)} cases")
    per_length_cases = {}
    for (length, _case) in groups_all:
        per_length_cases[length] = per_length_cases.get(length, 0) + 1
    print("Cases per length:", {l: per_length_cases.get(l, 0) for l in LENGTHS})

    scorers_by_length = {}
    tot_total = tot_has = tot_no = tot_miss_base = tot_miss_grp = 0
    for held_out in LENGTHS:
        train_groups = {k: v for k, v in groups_all.items() if k[0] != held_out}
        test_keys = [k for k in groups_all if k[0] == held_out]

        scorer, final_loss = fit_grouped(
            train_groups, epochs=args.epochs, lr=args.lr, seed=args.seed,
            entropy_lambda=args.entropy_lambda, val_frac=args.val_frac,
            patience=args.patience, eval_every=args.eval_every,
        )
        if scorer is None:
            print(f"\nL{held_out}: no pairwise training pairs available -- skipped")
            continue
        scorers_by_length[held_out] = scorer

        n_correct, n_total = eval_scorer(scorer, groups_all, test_keys)
        n_base_correct, n_base_total = eval_baseline(groups_all, test_keys)
        n_has, n_missed, n_no = missed_cases_scorer(scorer, groups_all, test_keys)
        n_has_b, n_missed_b, n_no_b = missed_cases_baseline(groups_all, test_keys)

        print(f"\n{'=' * 78}")
        print(f"Held-out length {held_out}  (trained on lengths "
              f"{[l for l in LENGTHS if l != held_out]}, final train loss={final_loss:.4f})")
        print("=" * 78)
        for name, vals in scorer.resolved_weights().items():
            print(f"  {name:<38}" + "  ".join(f"{v:.4f}" for v in vals))
        if n_total:
            print(f"\nAccuracy on held-out L{held_out} cases: "
                  f"grouped {n_correct}/{n_total} ({100 * n_correct / n_total:.1f}%)"
                  f"  vs equal-weight score_1 baseline "
                  f"{n_base_correct}/{n_base_total} ({100 * n_base_correct / n_base_total:.1f}%)")
        print(f"Missed (correct exists, not selected): grouped {n_missed}/{n_has}"
              f"  vs equal-weight {n_missed_b}/{n_has_b}  (no_correct_avail={n_no})")

        tot_total += n_total
        tot_has += n_has
        tot_no += n_no
        tot_miss_base += n_missed_b
        tot_miss_grp += n_missed

    print(f"\n{'=' * 78}")
    print(f"TOTAL across all {len(scorers_by_length)} held-out lengths")
    print("=" * 78)
    print(f"no_correct_avail (unfixable): {tot_no}")
    print(f"has_correct: {tot_has}")
    print(f"missed -- equal-weight baseline: {tot_miss_base}")
    print(f"missed -- grouped (nested-simplex) model: {tot_miss_grp}")


if __name__ == "__main__":
    main()
