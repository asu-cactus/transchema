# Leaf-Feature Weight Tuning — Leave-One-Length-Out

Extends the flat-4-component weight fitting in `SCORE_WEIGHTS_ANALYSIS.md`
(Method C: pairwise ranking logistic regression) to a **16-feature leaf-level
decomposition** of `score_1`, fit **per problem length**, with a
leave-one-length-out evaluation so the reported accuracy always measures
generalization to lengths the model never trained on.

Two scripts implement this, run in order:

1. `collect_scraped_script_scores.py` → `scraped_scripts/scraped_scripts_scores.csv`
2. `fit_weights_leave_one_length_out.py` → the 6 weight vectors + all results below

---

## 1. Data pipeline

`collect_scraped_script_scores.py` scores every script under
`scraped_scripts/L{1,2,3,4,5,9}/` (already de-duplicated by distinguishing
score) against its case's ground truth:

- **TRAIN run**: script executed as-is (reads `training_N.csv`), scored with
  `value_based_relative_csv_score` against `target.csv` — this mirrors what
  MCTS itself sees as reward during search.
- **TEST run**: script rewritten to read `test_N.csv` instead, executed, and
  its output compared to `target.csv` via `compare_tables_matching`
  (autopipeline hard match) — this produces the `is_match` **label** used for
  training and evaluation below. It is a held-out generalization signal, not
  something the TRAIN-side score ever sees.

**No redundant work**: FD mining and the self-column-map on the ground truth
depend only on `target.csv`, never on any particular script — so they're
computed **once per case** and reused across every script belonging to that
case (mirrors `Langraph/mcts_search.py`'s `_gt_score_cache_worker`), instead
of once per script.

**Wide-table guard**: a case is discarded entirely (no FD-mining attempt, no
script execution) if its ground truth has more than 30 columns — avoids
paying for an FD-mining timeout that would happen anyway on cases too wide to
score meaningfully.

### Run stats

| | Count |
|---|---|
| Total script rows | 3,310 |
| Rows with successful TRAIN-side scoring (`fd_f1` present) | 3,156 |
| Rows with successful TEST-side validation (`is_match` present) | 3,152 |
| `is_match = True` | 554 |
| `is_match = False` | 2,598 |
| Cases discarded (GT > 30 columns) | 23 (L1:2, L2:1, L3:4, L4:5, L5:3, L9:8; largest: 520-col case) |

---

## 2. Feature vector — 16 leaf signals

`score_1`'s old 4 components (`fd_f1`, `avg_col_score_1`, `row_count_score`,
`max_missing_score`) collapse two different kinds of averaging into one
number each: `fd_f1` blends precision and recall via a fixed harmonic mean,
and `avg_col_score_1` blends every GT column together regardless of type. The
leaf feature set un-collapses both:

| Feature | Meaning | Source column type |
|---|---|---|
| `precision` | FD precision (`tp / len(gen_fds)`) | fd_f1's replacement, half 1 |
| `recall` | FD recall (`tp / len(truth_fds)`) | fd_f1's replacement, half 2 |
| `avg_float_js` | mean JS similarity | float numeric columns |
| `avg_float_range` | mean range overlap | float numeric columns |
| `avg_int_js` | mean JS similarity | integer numeric columns |
| `avg_int_range` | mean range overlap | integer numeric columns |
| `avg_int_nunique` | mean uniqueness-ratio similarity | integer numeric columns |
| `avg_int_missing` | mean missing-fraction similarity | integer numeric columns |
| `avg_id_nunique` | mean uniqueness-ratio similarity | id columns |
| `avg_id_missing` | mean missing-fraction similarity | id columns |
| `avg_cat_prop` | mean structural property-score | categorical columns |
| `avg_cat_nunique` | mean uniqueness-ratio similarity | categorical columns |
| `avg_cat_missing` | mean missing-fraction similarity | categorical columns |
| `avg_date_score` | mean matched-date score (mismatches fold in as 0) | date columns |
| `row_count_score` | `min(n_gen, n_gt) / max(n_gen, n_gt)`, raw row counts | table-level |
| `max_missing_score` | worst-column missing-fraction agreement | table-level |

**Missing-type convention**: if a script's output table has zero columns of a
given type (e.g. no `id` columns), that type's leaf features are imputed as
**0** — "no columns of this type" is treated as distinct from "columns of
this type scored perfectly," and keeps the pairwise-difference math
well-defined without per-row masking.

`avg_date_score` isn't split into JS/range like the numeric types are — the
underlying scoring code (`_compute_column_scores` in
`eval_score_value_based.py`) only exposes a pre-blended value for date
columns, not the separate components, and this pipeline reuses that code
rather than duplicating its internals.

---

## 3. Training process — pairwise ranking logistic regression

The actual selection objective isn't "is this script individually good" —
it's "does the search's own reward function rank the correct script above
the incorrect ones **within the same case**." Pointwise regression (fit
`P(is_match | x)` treating scripts as i.i.d.) never sees that comparison.
Pairwise ranking regression fits it directly:

For every case with at least one correct script (`is_match=True`) and at
least one incorrect script (`is_match=False`) in the training pool, form
every ordered `(correct, wrong)` pair and build **two** symmetric training
examples per pair:

```
z⁺ = x(correct) − x(wrong),   label = 1     (correct should outscore wrong)
z⁻ = x(wrong) − x(correct),   label = 0     (the reverse)
```

Then fit `LogisticRegression(fit_intercept=False)` on the stacked `z`
vectors — no intercept, since feature differences are naturally zero-centered.
This is equivalent to `P(r beats q) = sigmoid(w·(x_r − x_q))`, a linear
Bradley-Terry / RankNet-style pairwise preference model, and is the
logistic-loss relaxation of a max-margin ranking LP (same idea, smooth
exponential penalty instead of a piecewise-linear hinge). See
`SCORE_WEIGHTS_ANALYSIS.md` §6 for the original 4-feature version of this
same method (there called "Method C" — the best of the three approaches
tried, and the only one carried forward here).

Cases with **zero** correct scripts anywhere contribute no pairs (there's
nothing to rank against) and are excluded from training, but still count in
evaluation (see below) since MCTS genuinely failing to generate a correct
script is a real outcome, just not one any weight vector can fix.

---

## 4. Evaluation methodology

**Leave-one-length-out**: for each length `L ∈ {1,2,3,4,5,9}`, the pairwise
model is trained on every `(case, script)` pair from the other 5 lengths
combined, then evaluated **only** on `L`'s own cases. This measures whether a
weighting learned from other problem lengths transfers to a new one — a
stricter and more realistic test than a random split within the same length,
since it never lets the model see any case shape from the length it's being
scored on.

**Two metrics reported per length:**

- **Accuracy**: fraction of cases where `argmax_s w·x(s)` is a correct
  script (the same definition as `SCORE_WEIGHTS_ANALYSIS.md` §1).
- **Missed-cases breakdown**: splits every case into (a) no correct script
  exists among *any* candidate — unfixable by any weighting, and (b) a
  correct script exists but the argmax pick isn't it — the only bucket where
  reweighting can possibly help. Reported for both equal-weight `score_1`
  and the leave-one-out fitted weights, so the *actual* opportunity for
  improvement (bucket (b) only) is visible, not diluted by bucket (a).

---

## 5. Results — 6 leave-one-length-out weight vectors

Raw coefficients (from `LogisticRegression(fit_intercept=False)`, unconstrained
— sign and magnitude are both meaningful, no forced non-negativity or
sum-to-1, per the "accept the flat fit" decision made earlier in this
investigation):

| feature | L1 | L2 | L3 | L4 | L5 | L9 |
|---|---|---|---|---|---|---|
| precision | 1.5056 | 1.4629 | 1.4821 | 1.6491 | 2.0499 | 1.7185 |
| recall | 1.4484 | -0.1105 | 0.9759 | 0.7538 | 0.3719 | 0.5209 |
| avg_float_js | 1.5792 | 1.8007 | 0.8147 | 2.0851 | 2.1529 | 1.6269 |
| avg_float_range | 1.2927 | 1.1764 | 2.0188 | 1.2391 | 1.0734 | 2.0082 |
| avg_int_js | 0.1084 | 1.2331 | 0.7096 | 0.8411 | 0.9446 | 0.4724 |
| avg_int_range | 4.1152 | 2.7711 | 3.2021 | 3.3105 | 3.3570 | 3.7933 |
| avg_int_nunique | 5.2483 | 4.1003 | 4.3858 | 4.3845 | 4.4520 | 3.6992 |
| avg_int_missing | 0.4419 | 1.8032 | 0.7544 | 0.7166 | 0.7636 | 0.6867 |
| avg_id_nunique | 2.6910 | 2.1111 | 2.5835 | 2.8951 | 3.1275 | 2.8747 |
| avg_id_missing | 0.3668 | 0.7185 | 0.4666 | 0.5841 | 0.5842 | 0.6630 |
| avg_cat_prop | -1.7768 | -0.8872 | 1.5349 | 0.0222 | 0.2430 | -0.1128 |
| avg_cat_nunique | 2.8174 | 3.0294 | 2.1186 | 2.6189 | 2.5105 | 2.7631 |
| avg_cat_missing | 1.2435 | 0.9745 | 0.4703 | 1.0205 | 1.3220 | 1.0392 |
| avg_date_score | 0.2360 | 0.4916 | 0.4168 | 0.4505 | 0.4988 | 0.2854 |
| row_count_score | 3.2828 | 3.3626 | 4.2525 | 2.8468 | 3.1040 | 2.7334 |
| max_missing_score | 3.4635 | 3.6648 | 4.3352 | 4.1870 | 3.7548 | 3.8149 |

Each column was trained on the other 5 lengths (e.g. the L1 column was
trained on L2+L3+L4+L5+L9 combined, then evaluated only on L1's cases).

### Accuracy: leave-one-out weighted vs. equal-weight `score_1` baseline

| Held-out | Pairwise-LR | Equal-weight baseline | Δ |
|---|---|---|---|
| L1 | 74/97 (76.3%) | 80/97 (82.5%) | **-6.2 pts** |
| L2 | 76/99 (76.8%) | 75/99 (75.8%) | +1.0 pts |
| L3 | 71/96 (74.0%) | 68/96 (70.8%) | +3.2 pts |
| L4 | 34/85 (40.0%) | 34/85 (40.0%) | 0 (tied) |
| L5 | 45/95 (47.4%) | 42/95 (44.2%) | +3.2 pts |
| L9 | 71/91 (78.0%) | 66/91 (72.5%) | +5.5 pts |

### Missed-cases breakdown (correct script exists but not selected)

| Length | Total cases | No correct script exists (unfixable) | Has ≥1 correct script | Missed — equal-weight | Missed — weighted |
|---|---|---|---|---|---|
| L1 | 97 | 5 | 92 | 12 | **18** |
| L2 | 99 | 13 | 86 | 11 | 10 |
| L3 | 96 | 15 | 81 | 13 | 10 |
| L4 | 85 | 45 | 40 | 6 | 6 |
| L5 | 95 | 46 | 49 | 7 | 4 |
| L9 | 91 | 16 | 75 | 9 | 4 |
| **Total** | **563** | **140** | **423** | **58** | **52** |

Of the 423 cases where a correct script genuinely exists among the
candidates, the leave-one-out weighted model recovers 6 more of them than
equal weights (52 missed vs. 58) — but that net gain is entirely produced by
L3/L5/L9; L1 gets **worse**, and L2/L4 are roughly a wash.

---

## 6. L1 deep dive

L1 is the one length where the leave-one-out weighting actively hurts
(76.3% vs. 82.5% baseline, 18 vs. 12 missed). Three additional experiments
probed why:

| Training data used for L1's weights | Evaluated on | Accuracy | Missed (has-correct only) |
|---|---|---|---|
| Equal-weight `score_1` (no learning) | all 97 L1 cases | 80/97 (82.5%) | 12/92 |
| All 5 other lengths (L2,L3,L4,L5,L9) | all 97 L1 cases | 74/97 (76.3%) | 18/92 |
| L2+L3 only | all 97 L1 cases | 75/97 (77.3%) | 17/92 |
| **L1's own data** (78-case train / 19-case held-out split, seed 42) | 19 held-out L1 cases | 17/19 (89.5%) | 1/18 |
| Equal-weight `score_1`, same 19-case slice (for apples-to-apples comparison) | 19 held-out L1 cases | 17/19 (89.5%) — **tied** | 1/18 — **tied** |

Narrowing the training pool to L2+L3 only gives a small improvement over
using all 5 other lengths (17 missed vs. 18) but still underperforms equal
weights. Training purely on L1's own data ties equal weights exactly on
both the held-out and in-sample slices — checking the actual per-case picks
confirmed this isn't a coincidence of the accuracy count: **18 of the 19
held-out cases pick the literal same script** under both weightings; the
19th picks a different script, but it's correct either way.

**Conclusion**: L1 doesn't have enough of its own data (78 training cases →
only 252 pairwise pairs, against 16 features) to learn weights that
meaningfully diverge from equal weighting, and no other length's data
transfers to it. **Recommendation: keep equal weights for L1** specifically,
rather than deploying any of the learned vectors above for it.

---

## 7. Caveats

- **`avg_cat_prop` sign flips across lengths** (-1.78 for L1, -0.89 for L2,
  -0.11 for L9, but +1.53 for L3, +0.02 for L4, +0.24 for L5). A feature
  whose learned sign depends on which lengths are in the training pool is a
  symptom of the jump from 4 to 16 parameters outrunning the available data
  (~85-99 cases per held-out length) — treat this particular weight with
  skepticism before hardcoding it anywhere.
- **Consistently dominant across all 6 fits**: `avg_int_nunique`,
  `avg_int_range`, `row_count_score`, and `max_missing_score` — each
  routinely lands 0.10-0.17 normalized weight regardless of which lengths
  are held out. This echoes the original 4-feature finding in
  `SCORE_WEIGHTS_ANALYSIS.md` that row-count/missing-value integrity signals
  carry a disproportionate share of the real discriminating power.
- **L4's ceiling is a search problem, not a scoring problem**: the tie at
  40.0% for both weightings matches `SCORE_WEIGHTS_ANALYSIS.md` §7's earlier
  finding that 53% of L4 cases never had a correct script generated at all
  regardless of scoring — no weight vector can select a script that was
  never produced by MCTS in the first place.
- These are unconstrained logistic-regression coefficients (see the earlier
  "accept the flat fit" discussion) — they don't sum to 1 or stay
  non-negative by construction, so they should be read as relative
  importances (via the normalized column), not literal blend ratios.

---

## 8. Reproducing this

```bash
source env/bin/activate
python3 collect_scraped_script_scores.py           # ~1-2 hrs, only needed once (or after re-scraping scripts)
python3 fit_weights_leave_one_length_out.py         # seconds; prints all tables above
```

| File | Purpose |
|---|---|
| `collect_scraped_script_scores.py` | Scores every scraped script (TRAIN + TEST variants) → `scraped_scripts/scraped_scripts_scores.csv` |
| `scraped_scripts/scraped_scripts_scores.csv` | 3,310 rows — one per (length, case, script), all 16 leaf features + `is_match` label |
| `fit_weights_leave_one_length_out.py` | Fits the 6 leave-one-length-out weight vectors, prints accuracy + missed-cases tables |
