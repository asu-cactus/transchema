# Tuning HYBRID_C's weights and frequency coefficient C

## Background

HYBRID_C is MCTS's best-performing final-script-selection method. For every
unique script `i` seen during a case's search:

```
score(i)  = w1*fd_f1 + w2*avg_col_score_1 + w3*row_count_score + w4*max_missing_score
hybrid(i) = score(i) - C / sqrt(freq(i))
```

`freq(i)` counts how often a script's rounded score recurred across every
scored event in that case's log (sim + critique, every iteration, not
deduplicated) — a script whose score kept reappearing during search is
trusted more than a one-off. The original, hand-picked formula uses
**equal weights (0.25 each)** and **C=0.1**, giving the trusted real,
script-execution-validated baseline: **L1 84/100, L4 39/86, L9 68/101**
(combined 191/287).

The question across this whole effort: can `w` and/or `C` be *fit* rather
than hand-picked, to make HYBRID_C pick the correct script more often?

`freq` is always treated as a **fixed, historical fact** throughout —
it's determined by whatever scores the live MCTS search actually produced
(under equal weights, since that's what generated the logs), never
recomputed under a candidate `w` or `C`. This was an explicit, deliberate
simplification (not an approximation we settled for) — see
`fit_hybrid_weights_freq_logreg.py`'s docstring for the reasoning.

## Round 1 — fit `w`, hold `C=0.1` fixed

**File:** `fit_hybrid_weights_freq_logreg.py`

An earlier attempt (plain "Method C" in `SCORE_WEIGHTS_ANALYSIS.md`) fit `w`
via pairwise ranking logistic regression while ignoring `freq` entirely —
it improved plain best-score ranking but *hurt* HYBRID_C. Round 1 fixed
this by fitting `w` against a pairwise loss that already accounts for the
fixed `C=0.1` offset:

```
want: w.x_r - C/sqrt(freq_r)  >  w.x_q - C/sqrt(freq_q)   for every (correct r, wrong q) pair
  ⟺   w.(x_r - x_q)  >  C.(1/sqrt(freq_r) - 1/sqrt(freq_q))     [a known, fixed offset]
```

Logistic regression with a per-sample fixed offset (`P(r beats q) =
sigmoid(w.z - offset)`), L2-regularized (unregularized diverges — see
below), fit on the 273-case `score_regression_dataset.csv` pool.

**Result:** held-out accuracy never beat equal-weight anywhere across an
L2 sweep from 0 to 5000 — best case was an *exact tie* (40/53). Real
script-execution validation on the full 273-case pool gave weight-set-1
(`fd_f1=0.1241, avg_col_score_1=0.2487, row_count_score=0.3562,
max_missing_score=0.2710`) **190–192/287** depending on exact fit variant —
tied with or marginally above equal-weight's 191/287, never a robust win.

## Round 2 — jointly fit `w` AND `C`

**File:** `fit_hybrid_c_and_weights_freq_logreg.py`

`C` was never tuned, only inherited from the original hand-picked `0.1`.
Key trick: `hybrid(i) = w.x_i - C/sqrt(freq_i)` is linear in an **augmented
5-dim feature vector** `y_i = [x_i, 1/sqrt(freq_i)]`, with `hybrid(i) =
w.x_i + w5.x5_i` where `w5 = -C`. Fitting `w5` freely alongside `w1..w4`
via ordinary pairwise logistic regression (no fixed offset needed this
time) directly recovers a fitted `C = -w5` — the exact same model family
as Round 1, just one dimension bigger.

**Result of the L2 sweep:** held-out accuracy again never beat
equal-weight — best case was again an exact tie (40/53), this time at
`l2=0` (no regularization), where **C came out to ~5.07 — about 50x the
original hand-picked 0.1**. Real execution on the full 273-case pool:
`(w*, C*) = (3.7339, 9.3965, 10.9154, 8.0559; C=5.0728)` → HYBRID_C
**191/287**, an exact tie with equal-weight, while causing a real
regression on LCB_C=0.5 (186→171).

Auditing the fitted `w*` normalized to sum=1 (`fd_f1≈0.116,
avg_col_score_1≈0.293, row_count_score≈0.340, max_missing_score≈0.251`)
showed it's **nearly identical in direction** to weight-set-1's own ratios
(`0.124/0.249/0.356/0.271`) — the much larger raw magnitudes and the much
larger `C*` scale up together, so the ratio that actually drives argmax
decisions barely moved. This was independently confirmed empirically: on
a live 60-case subset, rescoring weight-set-1's own search with the new
`(w*, C*)` reproduced **the exact same picks, case for case**, as
weight-set-1's native HYBRID_C.

## Live validation experiments (real MCTS search, not replay)

Beyond the cached-dataset fits above, live `det_score_value` MCTS runs
were launched with `--score_weights` (added to `eval_score_value_based.py`
/ `Langraph/nodes.py` / `Langraph/mcts_search.py` this round — backward
compatible, defaults to equal weights) to test actual search behavior
under each weight vector, not just post-hoc rescoring of existing logs.
Every log now also carries the 4 raw unweighted components
(`components={fd_f1=.., avg_col_score_1=.., row_count_score=.., max_missing_score=..}`)
regardless of which weights drove the run, so any weight vector's HYBRID_C
can be recomputed from a log after the fact without rerunning search.

**60-case subset** (20 L1 + 20 L4 + 20 L9, fixed seed=42 sample), all three
weight vectors driving both search and HYBRID_C natively:

| | BEST_SCORE | OLD_total_reward | Q_VALUE | LCB_C=0.5 | HYBRID_C=0.1 |
|---|---|---|---|---|---|
| Equal-weight | 36/60 | **41/60** | 35/60 | **41/60** | 38/60 |
| Weight-set-1 (Round-1 fit, C=0.1) | 37/60 | 35/60 | 33/60 | 35/60 | **39/60** |
| Weight-set-2 (earlier freq-aware fit, C=0.1) | 31/60 | 34/60 | 31/60 | 34/60 | 35/60 |

Equal-weight actually **wins outright** on two of the five methods; weight-set-1's
HYBRID_C edge is a single case, within noise for 60 cases; weight-set-2 is
worse than both on every method.

**Full pool** (100 L1 + 100 L4 + 101 L9, weight-set-1 driving search),
HYBRID_C native vs. rescored with the Round-2 `(w*, C*)`:

| | L1 | L4 | L9 | Combined |
|---|---|---|---|---|
| Native (weight-set-1, C=0.1) | 84/100 | 37/96 | 72/99 | 193/295 |
| Rescored (w\*, C\*=5.0728) | 83/100 | 38/96 | 72/99 | 193/295 |

Identical combined total — a few cases flip in opposite directions
(L1 loses 1, L4 gains 1) but net to zero.

## Bottom line

Across two full fitting rounds (weights-only, then weights+C jointly),
three real live-search experiments, and both cached-dataset and
real-execution validation: **no reweighting of the 4 score_1 components,
with or without a jointly-tuned frequency coefficient, produces a robust
improvement over the original equal-weight, C=0.1 formula.** Every variant
lands within 1-2 cases of equal-weight on HYBRID_C, and several
underperform it on the other four selection methods.

A follow-up audit (`audit_wrong_cases_scoring_failure.py`) explains why:
of the cases where HYBRID_C picks wrong, real re-execution of *every*
unique script tried in the search showed **only ~10% are genuine ranking/
scoring failures** (a correct script existed but wasn't ranked top) — the
other ~90% never had a correct script generated anywhere in the search at
all, for any weight vector to possibly select. Confirmed directly: rerunning
those unsolved cases with a stronger model (o4-mini vs gpt-4.1-mini, same
weights) recovered a substantial fraction of them outright (9/20 on an L2
subset). **The scoring formula is not the bottleneck — search/model
generation coverage is.**

## Key files

| File | Purpose |
|---|---|
| `fit_hybrid_weights_freq_logreg.py` | Round 1: fit `w`, `C=0.1` fixed (offset-based pairwise LR). |
| `fit_hybrid_c_and_weights_freq_logreg.py` | Round 2: jointly fit `w` and `C` (5-dim augmented pairwise LR + L2 sweep). |
| `fit_hybrid_weights_lp.py` | Shared: fixed-freq dataset builder (`build_case_data`), self-consistent evaluator, LP baseline (not recommended — see `SCORE_WEIGHTS_ANALYSIS.md`). |
| `evaluate_weights_real.py` | Real script-execution validation on the 273-case pool, equal-weight vs. weight-set-1 vs. Round-2 `(w*, C*)`. |
| `rescore_hybrid_weightset1_with_weightset2.py`, `rescore_hybrid_weightset1_with_new_wc.py` | Post-hoc rescoring of a live run's logged components under a different weight vector, without rerunning search. |
| `run_score_weights_60cases.sh`, `run_l1_l4_l9_weights_full.sh`, `run_l2_weights_100cases.sh`, `run_l3_l5_weights.sh` | Live MCTS launchers per weight vector / length, using `--score_weights`. |
| `analyze_score_weights_60cases_all_methods.py`, `analyze_l1_l4_l9_full_weights_all_methods.py`, `analyze_l1_l4_l9_full_both_hybrid.py` | 5-method / both-hybrid-variant real-execution analysis of a live run's logs. |
| `audit_wrong_cases_scoring_failure.py` | Per-case audit: is a HYBRID_C miss a real ranking failure, or was no correct script ever generated? |
| `Langraph/nodes.py`, `Langraph/mcts_search.py`, `eval_score_value_based.py` | `--score_weights` plumbing + raw-component logging added this round (backward compatible, default = equal weights). |
