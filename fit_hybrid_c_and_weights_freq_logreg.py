"""
fit_hybrid_c_and_weights_freq_logreg.py
===========================
Generalizes fit_hybrid_weights_freq_logreg.py: instead of holding HYBRID_C's
frequency coefficient fixed at 0.1 and only fitting the 4 score_1 component
weights, this jointly fits BOTH -- w (4 components) and C (the weight on
the frequency term) -- via a single pairwise ranking logistic regression.

Key trick: hybrid(i) = w.x_i - C/sqrt(freq_i) is linear in an augmented
5-dim feature vector y_i = [x_i, 1/sqrt(freq_i)], with hybrid(i) = w.x_i +
w5.x5_i where w5 = -C. So fitting w5 freely alongside w1..w4 via ordinary
pairwise logistic regression (no fixed offset needed this time -- that
machinery was only required when C was pinned at a known constant) directly
recovers a fitted C = -w5. Same L2-regularized MLE as
fit_hybrid_weights_freq_logreg.fit_offset_logreg, just with offsets=0.

freq_i is unchanged from the prior round: a FIXED, historical fact from
build_case_data (the original equal-weight live-search log scores), never
recomputed under any candidate w or C.

Usage: python3 fit_hybrid_c_and_weights_freq_logreg.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import numpy as np

from fit_hybrid_weights_lp import (
    load_component_lookup, build_case_data, FEATURES, EQUAL_W, C_HYBRID,
)
from fit_hybrid_weights_freq_logreg import split_cases, fit_offset_logreg

AUG_FEATURES = FEATURES + ["inv_sqrt_freq"]


def build_augmented_pairs(case_data, keys):
    """Same symmetric pairwise construction as
    fit_hybrid_weights_freq_logreg.build_pairs, but on 5-dim y = [x, 1/sqrt(freq)]
    vectors with NO fixed offset -- C is recovered from the 5th coefficient,
    not baked in as a known constant."""
    Z, y, sw = [], [], []
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
            y_r = np.append(x_r, 1.0 / np.sqrt(f_r))
            for x_q, f_q in wrong:
                y_q = np.append(x_q, 1.0 / np.sqrt(f_q))
                Z.append(y_r - y_q); y.append(1); sw.append(pair_weight)
                Z.append(y_q - y_r); y.append(0); sw.append(pair_weight)
    return (np.array(Z), np.array(y, dtype=float), np.array(sw, dtype=float), n_informative)


def eval_fixed_freq_accuracy_variable_c(w, C, case_data):
    """Same as fit_hybrid_weights_lp.eval_fixed_freq_accuracy but with C as
    an argument instead of the hardcoded module constant -- needed since C
    is no longer fixed at 0.1 here."""
    per_length = {}
    n_ok = n_total = 0
    for (length, case_num), case_list in case_data.items():
        best = max(case_list, key=lambda t: float(np.dot(w, t[0])) - C / np.sqrt(t[2]))
        ok = best[1]
        n_total += 1
        n_ok += bool(ok)
        pl = per_length.setdefault(length, [0, 0])
        pl[1] += 1
        pl[0] += bool(ok)
    return n_ok, n_total, per_length


def report(name, w4, C, case_data, keys):
    subset = {k: case_data[k] for k in keys if k in case_data}
    ok, n, per_length = eval_fixed_freq_accuracy_variable_c(w4, C, subset)
    breakdown = "  ".join(f"L{l}={v[0]}/{v[1]}" for l, v in sorted(per_length.items()))
    print(f"  {name:<20}: {ok}/{n} ({100*ok/max(n,1):.1f}%)   [{breakdown}]")
    return ok, n


def main():
    comp_lookup = load_component_lookup()
    print(f"Component lookup covers {len(comp_lookup)} cases")
    case_data = build_case_data(comp_lookup)
    print(f"Built per-case data for {len(case_data)} cases\n")

    train_keys, test_keys = split_cases(case_data)
    print(f"Train cases: {len(train_keys)}, Held-out cases: {len(test_keys)}\n")

    Z, y, sw, n_informative = build_augmented_pairs(case_data, train_keys)
    print(f"{len(Z)} pairwise training examples across {n_informative} informative train cases\n")

    offsets = np.zeros(len(y))  # no fixed offset -- C is learned as w5

    print(f"{'='*90}\nL2 sweep (5-dim fit: w1..w4 + w5, C_fitted = -w5)\n{'='*90}")
    print(f"{'l2':>8}  {'||w||':>8}  {'C_fitted':>10}  {'held-out':>14}  {'train':>14}  {'all':>14}")

    best = None  # (held_out_ok, l2, w5vec, C)
    for l2 in [0, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 5000]:
        w5vec = fit_offset_logreg(Z, offsets, y, sw, l2=l2)
        w4, C_fitted = w5vec[:4], -w5vec[4]
        ho_ok, ho_n, _ = eval_fixed_freq_accuracy_variable_c(w4, C_fitted, {k: case_data[k] for k in test_keys})
        tr_ok, tr_n, _ = eval_fixed_freq_accuracy_variable_c(w4, C_fitted, {k: case_data[k] for k in train_keys})
        all_ok, all_n, _ = eval_fixed_freq_accuracy_variable_c(w4, C_fitted, case_data)
        wn = np.linalg.norm(w5vec)
        print(f"{l2:>8}  {wn:>8.3f}  {C_fitted:>10.4f}  {ho_ok:>4}/{ho_n:<4}({100*ho_ok/ho_n:4.1f}%)  "
              f"{tr_ok:>4}/{tr_n:<4}({100*tr_ok/tr_n:4.1f}%)  {all_ok:>4}/{all_n:<4}({100*all_ok/all_n:4.1f}%)")
        if best is None or ho_ok > best[0]:
            best = (ho_ok, l2, w5vec, C_fitted)

    print(f"\nBest by held-out accuracy: l2={best[1]}, C_fitted={best[3]:.4f}")
    w4_best = best[2][:4]
    print(f"  weights: {dict(zip(FEATURES, np.round(w4_best, 4)))}")

    print(f"\n{'='*90}\nBaselines for comparison (equal-weight, C=0.1)\n{'='*90}")
    report("Equal-weight held-out", EQUAL_W, C_HYBRID, case_data, test_keys)
    report("Equal-weight all", EQUAL_W, C_HYBRID, case_data, case_data.keys())

    print(f"\n{'='*90}\nRefit on 100% of data (for final deployment), same best l2={best[1]}\n{'='*90}")
    Z_all, y_all, sw_all, n_inf_all = build_augmented_pairs(case_data, case_data.keys())
    offsets_all = np.zeros(len(y_all))
    w5vec_final = fit_offset_logreg(Z_all, offsets_all, y_all, sw_all, l2=best[1])
    w4_final, C_final = w5vec_final[:4], -w5vec_final[4]
    print(f"Final weights (100% fit): {dict(zip(FEATURES, np.round(w4_final, 4)))}")
    print(f"Final C_fitted (100% fit): {C_final:.4f}")
    report("Final (w*, C*) all", w4_final, C_final, case_data, case_data.keys())


if __name__ == "__main__":
    main()
