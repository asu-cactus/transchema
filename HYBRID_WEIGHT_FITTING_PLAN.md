# Fitting score_1 weights to preserve/improve HYBRID_C selection

## Background

`analyze_new_weights_all_methods.py` compares 5 different ways of picking a
final script out of an MCTS search tree, re-scored under a candidate weight
vector without re-running any scripts (it reuses the (fd_f1, avg_col_score_1,
row_count_score, max_missing_score, is_match) already cached in
`score_regression_dataset.csv`, looked up by the script's original log score):

- `BEST_SCORE` — global max score anywhere in the log.
- `OLD_total_reward` — greedy total-reward tree path, leaf's best.
- `Q_VALUE` — greedy `total_reward/visits` tree path, leaf's best.
- `LCB_C=0.5` — greedy path using `q − 0.5/√visits` (lower-confidence-bound) at each split.
- `HYBRID_C=0.1` — see below.

Under the pairwise-LR weights fit earlier (`fd_f1=0.1241, avg_col_score_1=0.2487,
row_count_score=0.3562, max_missing_score=0.2710`), L1 (100 training cases)
moved like this vs. the current equal-weight (0.25 each) formula:

| Method | Equal-weight | New-weight | Δ |
|---|---|---|---|
| BEST_SCORE | 78/100 | 79/100 | +1 |
| OLD_total_reward | 80/100 | 80/100 | 0 |
| Q_VALUE | 80/100 | 80/100 | 0 |
| LCB_C=0.5 | 82/100 | 81/100 | −1 |
| **HYBRID_C=0.1** | **85/100** | **82/100** | **−3** |

HYBRID_C is the best-performing method under the current formula, and the
BEST_SCORE-optimized weights make it *worse*. The fix: fit weights against
HYBRID_C's own selection criterion instead of plain BEST_SCORE argmax.

## What HYBRID_C actually computes

From `flat_hybrid_pick_new()` in `analyze_new_weights_all_methods.py`, for
every case: take every scored event in the log (every iteration's sim/critique
attempt — NOT deduplicated), and for the case's unique scripts pick the one
maximizing

```
hybrid(i) = score(i) − C / √freq(round(score(i), 4))
```

where `freq(s)` = how many scored events in that case's ENTIRE log (across
every iteration, sim and critique, not deduplicated) had a score rounding to
`s`. A script whose score value recurred often across the search is trusted
more (penalized less) than one whose score was a one-off.

## Why this can't be fit the same way as BEST_SCORE

The earlier pairwise-LR/LP fit only needed `w·x_correct > w·x_wrong` — a fixed
structure independent of `w` beyond the dot product itself. HYBRID_C breaks
this: **`freq` depends on `w`**. Changing `w` changes every script's score,
which changes which scripts round to the same 4-decimal value, which changes
`freq`, which changes the ranking again. It's a circular/fixed-point problem,
not a one-shot linear fit.

## Plan (single-pass, no iteration — start here before considering iterating)

1. **Freeze `freq` using the current equal-weight formula** (matching how the
   reported 85/100 baseline itself was measured): for every scored event in
   every case's log, compute `score = 0.25·fd_f1 + 0.25·avg_col_score_1 +
   0.25·row_count_score + 0.25·max_missing_score`, round to 4 decimals, count
   occurrences per case → `freq_i` for every unique script `i`. Treat these as
   fixed constants for this fitting pass.

2. **Reformulate the pairwise ranking constraint with that fixed offset.**
   For a correct/wrong pair `(r, q)` in the same case, wanting
   `hybrid(r) > hybrid(q)`:

   ```
   score(r) − C/√freq_r  >  score(q) − C/√freq_q
   w·x_r − w·x_q         >  C/√freq_r − C/√freq_q
   ```

   So the RANKING LP margin constraint from before becomes, with a per-pair
   constant offset added to the margin:

   ```
   w·x_r − w·x_q + ξ_{c,r,q}  ≥  1 + C·(1/√freq_r − 1/√freq_q)
   ```

   (previously just `≥ 1`). This is still linear in `w` — the offset is a
   known constant per pair, computed once in step 1 — so it drops straight
   into the same LP structure:

   ```
   minimize      Σ_c (1/(|Cc|·|Wc|)) Σ_{r∈Cc,q∈Wc} ξ_{c,r,q}
   subject to    w·x_r − w·x_q + ξ_{c,r,q}  ≥  1 + C·(1/√freq_r − 1/√freq_q)
                 ξ_{c,r,q} ≥ 0,   w1,w2,w3,w4 ≥ 0
   ```

   solved via `scipy.optimize.linprog`. (This offset does **not** fit into
   plain `sklearn.LogisticRegression` — per-sample additive offsets are a GLM
   "offset" feature that sklearn's logistic regression doesn't support; the
   LP handles it natively since it's just a constant on one side of an
   inequality.)

3. **Solve for `w`.**

4. **Evaluate honestly**: plug the fitted `w` into the *actual*, unmodified
   `flat_hybrid_pick_new` (real recomputed `freq` under the new `w`, not the
   frozen approximation from step 1) across all cases, and report the full
   5-method table (BEST_SCORE / OLD_total_reward / Q_VALUE / LCB_C=0.5 /
   HYBRID_C=0.1) so we can see whether HYBRID_C actually stops regressing —
   not just whether the surrogate LP objective improved.

5. **If the single pass doesn't hold up**, consider iterating: recompute
   `freq` under the newly-fit `w`, refit, repeat (fixed-point iteration) —
   but only after confirming the single pass isn't already good enough, since
   iterating adds real complexity/instability for a possibly marginal gain.

## Scope

Fit across **L1 + L4 + L9 combined** (not L1 only), reusing the same case
pool as `score_regression_dataset.csv` / the existing pairwise-LR fit, and
evaluate the resulting weights across all three lengths using
`analyze_new_weights_all_methods.py`'s existing lookup/rescoring machinery
(no changes needed there — `load_lookup(weights=...)` already accepts an
arbitrary weight dict).
