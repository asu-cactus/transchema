"""
fit_hybrid_weights_freq_logreg.py
===========================
Frequency-aware generalization of Method C (pairwise ranking logistic
regression, from SCORE_WEIGHTS_ANALYSIS.md) for the score_1 component
weights, so that HYBRID_C's own C=0.1 frequency-trust penalty is accounted
for at fit time -- plain Method C ignored it entirely, which is exactly why
it regressed HYBRID_C despite improving plain best-score argmax accuracy.

freq_i is a FIXED, historical fact -- computed once from the original
equal-weight log scores via fit_hybrid_weights_lp.build_case_data.
Changing the component weights changes the *score*, not which events the
live MCTS search actually recorded as recurring, so freq is never
recomputed under a candidate weight vector (no circularity, no iteration).

Model: for every case with a correct and a wrong unique script, every pair
(r correct, q wrong), we want

    w.x_r - C/sqrt(freq_r)  >  w.x_q - C/sqrt(freq_q)
    w.(x_r - x_q)           >  C.(1/sqrt(freq_r) - 1/sqrt(freq_q))   [a KNOWN, fixed offset]

This is logistic regression with a per-sample fixed offset:
    P(r beats q | z) = sigmoid(w.z - offset)
Same sigmoid/cross-entropy loss as fit_score_weights_regression.fit_pairwise,
generalized with the offset term (sklearn's LogisticRegression has no offset
parameter, so this is fit directly via scipy.optimize.minimize, L-BFGS-B).

Usage: python3 fit_hybrid_weights_freq_logreg.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import random
import numpy as np
from scipy.optimize import minimize

from fit_hybrid_weights_lp import (
    load_component_lookup, build_case_data, eval_fixed_freq_accuracy,
    FEATURES, EQUAL_W, C_HYBRID,
)

SEED = 42


def split_cases(case_data, test_frac=0.2, seed=SEED):
    """Split (length, case_num) keys 80/20, stratified by length -- same
    convention as fit_score_weights_regression.split_cases, adapted to
    case_data's int-keyed (length, case_num) tuples."""
    by_length = {}
    for (length, case_num) in case_data:
        by_length.setdefault(length, []).append(case_num)
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


def build_pairs(case_data, keys, C):
    """Symmetric pairwise (correct, wrong) examples with a fixed per-pair
    offset derived from the FIXED freq -- mirrors fit_pairwise's symmetric
    augmentation (z, offset, label=1) + (-z, -offset, label=0). Each pair is
    also given a sample_weight of 1/(|Cc|*|Wc|) so a case with many
    candidate scripts (hence many pairs) doesn't dominate the loss over a
    case with few -- same per-case normalization the LP formulation in
    fit_hybrid_weights_lp.py uses, needed because unweighted pairs otherwise
    let a few pair-heavy cases overwhelm the objective."""
    Z, offsets, y, sw = [], [], [], []
    n_informative = 0
    for key in keys:
        case_list = case_data.get(key)
        if not case_list:
            continue
        correct = [(x, f) for x, m, f in case_list if m]
        wrong = [(x, f) for x, m, f in case_list if not m]
        if not correct or not wrong:
            continue
        n_informative += 1
        pair_weight = 1.0 / (len(correct) * len(wrong))
        for x_r, f_r in correct:
            for x_q, f_q in wrong:
                offset = C * (1.0 / np.sqrt(f_r) - 1.0 / np.sqrt(f_q))
                Z.append(x_r - x_q); offsets.append(offset); y.append(1); sw.append(pair_weight)
                Z.append(x_q - x_r); offsets.append(-offset); y.append(0); sw.append(pair_weight)
    return (np.array(Z), np.array(offsets), np.array(y, dtype=float),
            np.array(sw, dtype=float), n_informative)


def fit_offset_logreg(Z, offsets, y, sample_weight, l2=0.0, w0=None):
    """P(y=1|z) = sigmoid(w.z - offset), fit by weighted maximum likelihood,
    with L2 shrinkage toward 0 (weight ratios still meaningful after
    normalizing). Without this, unregularized logistic regression on
    (near-)separable pairs diverges to arbitrarily large ||w|| chasing
    training-pair margins -- confirmed empirically here (loss drops
    148.6->37.6 while ||w|| grows to ~20), which overfits pairwise ranking
    noise rather than the actual case-level argmax accuracy we care about."""
    n, d = Z.shape
    if w0 is None:
        w0 = np.full(d, 0.25)

    def nll_and_grad(w):
        u = Z @ w - offsets
        s = (1 - 2 * y) * u
        loss = (sample_weight * np.logaddexp(0, s)).sum() + 0.5 * l2 * np.dot(w, w)
        p = 1.0 / (1.0 + np.exp(-u))
        grad = Z.T @ (sample_weight * (p - y)) + l2 * w
        return loss, grad

    res = minimize(nll_and_grad, w0, jac=True, method="L-BFGS-B")
    if not res.success:
        raise RuntimeError(f"Optimization failed: {res.message}")
    return res.x


def report(name, weights, case_data, keys):
    subset = {k: case_data[k] for k in keys if k in case_data}
    ok, n, per_length = eval_fixed_freq_accuracy(weights, subset)
    breakdown = "  ".join(f"L{l}={v[0]}/{v[1]}" for l, v in sorted(per_length.items()))
    print(f"  {name:<20}: {ok}/{n} ({100*ok/n:.1f}%)   [{breakdown}]")


def main():
    comp_lookup = load_component_lookup()
    print(f"Component lookup covers {len(comp_lookup)} cases")
    case_data = build_case_data(comp_lookup)
    print(f"Built per-case data for {len(case_data)} cases\n")

    train_keys, test_keys = split_cases(case_data)
    print(f"Train cases: {len(train_keys)}, Held-out cases: {len(test_keys)}\n")

    Z, offsets, y, sw, n_informative = build_pairs(case_data, train_keys, C_HYBRID)
    print(f"{len(Z)} pairwise training examples across {n_informative} informative train cases")

    w = fit_offset_logreg(Z, offsets, y, sw)
    print(f"\nFitted weights (frequency-aware pairwise logistic regression, C={C_HYBRID}):")
    for f, v in zip(FEATURES, w):
        print(f"  {f} = {v:.4f}")
    total = np.sum(np.abs(w))
    if total > 0:
        print("Normalized (sum|w|=1):", {f: round(v / total, 4) for f, v in zip(FEATURES, w)})

    print(f"\n{'='*70}\nHeld-out evaluation ({len(test_keys)} cases)\n{'='*70}")
    report("Equal-weight", EQUAL_W, case_data, test_keys)
    report("Freq-aware LR", w, case_data, test_keys)

    print(f"\n{'='*70}\nTrain evaluation ({len(train_keys)} cases, in-sample)\n{'='*70}")
    report("Equal-weight", EQUAL_W, case_data, train_keys)
    report("Freq-aware LR", w, case_data, train_keys)

    print(f"\n{'='*70}\nAll {len(case_data)} cases combined\n{'='*70}")
    report("Equal-weight", EQUAL_W, case_data, case_data.keys())
    report("Freq-aware LR", w, case_data, case_data.keys())


if __name__ == "__main__":
    main()
