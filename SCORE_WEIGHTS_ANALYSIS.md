# Score Weight Optimization — Full Writeup

## 1. What problem are we solving?

`eval_score_value_based.py` scores every generated pipeline script with `score_1`,
a **hardcoded equal-weight average** of four components:

```
score_1 = 0.25*fd_f1 + 0.25*avg_col_score_1 + 0.25*row_count_score + 0.25*max_missing_score
```

- `fd_f1` — functional-dependency F1 between generated output and ground truth.
- `avg_col_score_1` — average per-column similarity (numeric: min(range_overlap, JS
  similarity); categorical: property/Jaccard score; see `_compute_column_scores`
  in `eval_score_value_based.py`).
- `row_count_score` — `min(n_gen, n_gt) / max(n_gen, n_gt)`, catches row-count blowups
  (e.g. a reversed join direction).
- `max_missing_score` — `1 - |worst-column-missing-fraction(gen) - worst-column-missing-fraction(gt)|`.

This score is what MCTS uses as its **reward signal** during search, and (via
`global_best_score`/`global_best_script`) to pick the final script it hands back.
The question: **is 0.25/0.25/0.25/0.25 actually the best way to combine these four
signals, or can a learned weight vector pick the correct script more often?**

"Correct" here means: when you re-run the script on held-out **test** data and
compare its output to `target.csv` with `compare_tables_matching` (the codebase's
own strict "autopipeline" match), does it match exactly (`is_match=True`)?

The true objective we want to maximize is a **case-level, discrete count**:

```
accuracy(w) = (number of cases where argmax_s [w · components(s)] has is_match=True)
              --------------------------------------------------------------------
                                    (total number of cases)
```

i.e., for each case, sort its candidate scripts by the weighted score and check
whether the top one is actually correct. This is not a smooth/differentiable
function of `w` (it's an argmax + an indicator), so every fitting method below is
a **smooth surrogate** for it — we optimize something differentiable, then report
`accuracy(w)` afterward as the real metric that matters.

---

## 2. Building the dataset — `build_score_regression_dataset.py`

### 2.1 Where the scripts come from

For every case across three experiment lengths, we parse the MCTS log and pull
out **every unique Python script** that ever appeared in a `Simulate` or
`Critique` LLM turn (not just the one MCTS ended up choosing):

| Length | Log source | Cases |
|---|---|---|
| L1 | `logs_langraph/rag_det_score_run9_l1_pilot20/` (0-19) + `rag_det_score_run9_l1_batch_20to100/` (20-99) | 100 |
| L4 | `logs_langraph/test_script_4_l4/` | 100 |
| L9 | `logs_langraph/test_script_4_l9/` | 101 |

Extraction logic (`extract_all_scored_scripts`, reused from
`analyze_run8_failed_case_scripts.py`) walks each log line-by-line, tracks the
current MCTS iteration and LLM query type (`Query of Type : MCTS Simulate/Critique`),
and grabs the **last** fenced ```` ```python ```` block in each LLM response between
`Result Recieved :` and `Cost of the query`. Scripts are de-duplicated by exact
text within a case (a script that recurs across iterations is only run once).

### 2.2 What we do with each unique script — two separate executions

For every unique `(case, script)` pair, we run **two variants**, each writing its
output to a uniquely-named temp CSV (`target_multisource_mcts_<tag>_<uuid>.csv`)
so that concurrently-running scripts from the same case never collide on the
same hardcoded output filename:

1. **TRAIN run** — the script exactly as extracted (reads `training_N.csv`).
   Load its output + `target.csv`, call `value_based_relative_csv_score`, and
   record the **4 raw components** (`fd_f1`, `avg_col_score_1`, `row_count_score`,
   `max_missing_score`) plus the derived `score_1`/`score_2`/`row_ratio`. This
   mirrors exactly how MCTS itself computes reward during search — the training
   split is what the search sees and optimizes against.

2. **TEST run** — the same script with every `training_N.csv` path swapped to
   `test_N.csv` (`swap_training_to_test`). Load its output + `target.csv` and
   compute:
   - `is_match` — binary correctness label, via `compare_tables_matching`
     (`validation/hard_match.py` → `validation/autopipeline_match.py`'s
     `compare_tables`, the codebase's strict "autopipeline" matcher: exact row
     count + exact-value column matching with ~10% float tolerance).
   - `partial_reward` — continuous "how close did it get" signal, via
     `compare_tables_fuzzy` (`validation/fuzzy_match.py`): fraction of ground-truth
     columns that found *some* matching generated column, ignoring row-level
     correctness. This is literally what the codebase's own `reward_mode="partial"`
     uses elsewhere in `Langraph/nodes.py`.

This TRAIN/TEST split matters: **score components are computed on training data**
(exactly what MCTS reward reflects), but **correctness is judged on test data**
(the held-out generalization signal) — so the regression is honestly asking
"given what MCTS saw during search, which weighting best predicts what will
actually generalize?"

### 2.3 Output — `score_regression_dataset.csv`

One row per `(case, unique script)`:

```
length, case_num, iter, kind, log_score,
train_run_ok, train_error, fd_f1, avg_col_score_1, row_count_score,
max_missing_score, score_1, score_2, row_ratio, true_combined_score,
test_run_ok, test_error, is_match, partial_reward
```

`log_score` is kept only for reference/debugging — it's the reward the *original*
live MCTS run logged for that iteration, and it can legitimately disagree with our
freshly recomputed `score_1`. One concrete reason found during validation:
`Langraph/nodes.py`'s `_run_critique_llm` (line ~1886) initializes
`new_score = state["current_score"]` (the pre-critique score) and only overwrites
it if the critique script **executes successfully** — so a critique script that
fails to run silently inherits the old score in the log, even though its own
output was never actually scored. `log_score` is therefore not reliable evidence
of a *specific* script's quality; our recomputed columns are.

Raw yield: **1,192 script rows across 283 cases** (some rows have `train_run_ok`/
`test_run_ok = False` — broken/hallucinated scripts, e.g. referencing source
files that don't exist for that case). After filtering to rows with both runs
successful and all four components present ("clean rows"), we get **1,077 rows
across 273 cases** — this is the dataset every method below actually fits on.

---

## 3. The core difficulty: the true objective isn't directly optimizable

`accuracy(w)` (argmax + indicator, per case) has zero useful gradient almost
everywhere — you can't hand it to a regression solver. Three different smooth
surrogates were tried, from worst-aligned to best-aligned with the real goal.

---

## 4. Method A — LP: regress the weighted score onto `partial_reward`

**File:** `fit_score_weights_lp.py`

**Idea:** ignore per-case ranking entirely; just make the TRAIN-side weighted
score `w · x(s)` track the TEST-side `partial_reward(s)` as closely as possible,
in an L1 (least-absolute-deviation) sense, formulated as a linear program (LAD
regression is exactly representable as an LP via the classic split-into-two-
inequalities trick).

**Full formulation.** Let `x(s) = (fd_f1, avg_col_score_1, row_count_score,
max_missing_score)` for script `s`, and `pr(s) = partial_reward(s)`.

Variables: `w1, w2, w3, w4 ≥ 0` (the weights), `e_s ≥ 0` for every script `s`
(absolute-deviation slack).

```
minimize      Σ_s  e_s

subject to    e_s  ≥  pr(s) − w·x(s)        for every script s
              e_s  ≥  w·x(s) − pr(s)        for every script s
              w1 + w2 + w3 + w4  =  1        (normalization — fixes scale)
              w1, w2, w3, w4  ≥  0
              e_s ≥ 0
```

The two `e_s` constraints together force `e_s ≥ |pr(s) − w·x(s)|` (whichever side
is bigger dominates), and since the objective minimizes `Σ e_s`, the solver drives
`e_s` down to exactly that absolute gap. `Σ w_i = 1` is needed because otherwise
the LP is scale-free in the wrong direction here (shrinking all weights toward 0
also shrinks every gap toward `|pr(s)|`, which isn't obviously optimal or not —
practically, fixing the simplex constraint just gives an interpretable "weights
sum to 1" scale, unlike the margin-based LPs below). Solved exactly via
`scipy.optimize.linprog` (`method="highs"`), split 80/20 by case (stratified by
length, seed 42).

**Result — the solver found a degenerate solution:**

```
fd_f1 = 0.0000   avg_col_score_1 = 0.0000   row_count_score = 1.0000   max_missing_score = 0.0000
```

All weight went to `row_count_score`. It *does* reduce the stated LP objective
(mean absolute gap to `partial_reward`: train 0.4300→0.2591, test 0.4232→0.2626 —
a real improvement on the metric it was told to optimize), but on the metric that
actually matters it's **worse than the current equal-weight formula**:

| | Held-out (53 cases) | All 273 cases |
|---|---|---|
| Equal-weight | 41/53 (77.4%) `L1=16/19 L4=8/15 L9=17/19` | 178/273 (65.2%) `L1=78/99 L4=34/77 L9=66/97` |
| **LP-optimal** | **32/53 (60.4%)** `L1=13/19 L4=3/15 L9=16/19` | **159/273 (58.2%)** `L1=68/99 L4=22/77 L9=69/97` |

**Takeaway:** `partial_reward` (fuzzy column-match ratio) is not actually a great
stand-in for "is this the correct script within its case" — a script can match
columns well without matching values/rows, and `row_count_score` alone happens to
track the *fuzzy* signal best while being a poor discriminator of *exact* match.
This is a textbook case of optimizing the wrong loss: the surrogate metric
improved, the real one got worse. This method is **not recommended**.

---

## 5. Method B — Pointwise logistic regression

**File:** `fit_score_weights_regression.py` → `fit_pointwise`

**Idea:** treat every script as an i.i.d. sample, ignore which case it belongs
to, and fit `P(is_match=1 | x)` directly.

**Full formulation.**

```
P(y=1 | x) = sigmoid(w·x + b) = 1 / (1 + exp(-(w1·fd_f1 + w2·avg_col_score_1
                                                + w3·row_count_score + w4·max_missing_score + b)))

maximize (over w, b)   Σ_s [ y_s · log P(y_s=1|x_s) + (1−y_s) · log(1−P(y_s=1|x_s)) ]
```

i.e. standard maximum-likelihood logistic regression (`sklearn.linear_model.LogisticRegression`,
`fit_intercept=True`), fit on all 876 rows in the 220 train-split cases.

**Why this is a weak surrogate for the real goal:** the likelihood only asks "is
this script individually likely to be correct," never "does it beat the *other*
scripts in its own case." Two scripts in *different* cases with the same feature
vector get the same probability regardless of how their respective case-mates
look — the thing we actually care about (relative ranking within a case) never
enters the loss.

**Weights (raw / normalized to sum-of-abs = 1):**

| Component | Raw | Normalized |
|---|---|---|
| fd_f1 | 1.0209 | 0.1232 |
| avg_col_score_1 | 2.5232 | 0.3046 |
| row_count_score | 3.1333 | 0.3782 |
| max_missing_score | 1.6076 | 0.1940 |

**Result:**

| | Held-out (53 cases) | Train (220 cases, in-sample) |
|---|---|---|
| Equal-weight | 41/53 (77.4%) | 137/220 (62.3%) |
| Pointwise-LR | 41/53 (77.4%) — **identical** | 141/220 (64.1%) |

Ties the baseline exactly on held-out cases (same per-length breakdown too);
small in-sample-only gain.

---

## 6. Method C — Pairwise ranking logistic regression (the one that matters)

**File:** `fit_score_weights_regression.py` → `fit_pairwise`

**Idea:** a case has a discrepancy **iff at least one (correct, wrong) pair in
that case is mis-ordered** (`w·x_wrong ≥ w·x_correct`). So instead of predicting
correctness in isolation, directly fit a linear separator on **feature
differences between competing scripts in the same case** — this is the same
principle as the max-margin ranking LP below, just with a logistic (smooth,
off-the-shelf-solvable) loss instead of a hinge loss.

**Full formulation.** For every case `c` with correct-script set `Cc` and
wrong-script set `Wc` both non-empty, form every ordered pair `(r ∈ Cc, q ∈ Wc)`
and build two training examples per pair (symmetric augmentation so the classifier
sees both orderings):

```
z⁺ = x(r) − x(q),   label = 1     (correct should outscore wrong: want w·z⁺ > 0)
z⁻ = x(q) − x(r),   label = 0     (the reverse: want w·z⁻ < 0)

P(label=1 | z) = sigmoid(w·z)                      [no intercept — differences are
                                                      naturally zero-centered]

maximize (over w)   Σ_{pairs} [ label · log P(1|z) + (1−label) · log(1−P(1|z)) ]
```

This is exactly `LogisticRegression(fit_intercept=False)` fit on the stacked
`z` vectors — equivalent to fitting `P(r beats q) = sigmoid(w·(x_r − x_q))`, a
linear Bradley–Terry / RankNet-style pairwise preference model. It is the
logistic-loss relaxation of the hinge-loss max-margin LP:

```
minimize      Σ_c (1/(|Cc|·|Wc|)) Σ_{r∈Cc,q∈Wc} ξ_{c,r,q}
subject to    w·x(r) − w·x(q) + ξ_{c,r,q} ≥ 1     ∀ c, r∈Cc, q∈Wc
              ξ_{c,r,q} ≥ 0,   w1,w2,w3,w4 ≥ 0
```

(margin fixed at 1 to pin down scale, since ranking constraints are otherwise
scale-free). Both objectives penalize the same thing — how far `w·x(r) − w·x(q)`
falls short of separating correct from wrong — just with a smooth exponential
penalty (logistic) vs. a piecewise-linear one (hinge). The logistic version was
used in practice because it drops straight into `sklearn` with no custom LP solver
needed; the two are expected to behave very similarly here since neither
constraint set is exercised near a hard boundary.

**Weights (raw / normalized), fit on the 220-case train split:**

| Component | Raw | Normalized |
|---|---|---|
| fd_f1 | 1.8278 | 0.1241 |
| avg_col_score_1 | 3.6636 | 0.2487 |
| row_count_score | 5.2477 | 0.3562 |
| max_missing_score | 3.9922 | 0.2710 |

Compared to the current equal weights (0.25 each), this shifts weight *away*
from `fd_f1` and *toward* `row_count_score`/`max_missing_score`.

**Result:**

| | Held-out (53 cases) | Train (220 cases, in-sample) | All 273 cases |
|---|---|---|---|
| Equal-weight | 41/53 (77.4%) | 137/220 (62.3%) | 178/273 (65.2%) |
| **Pairwise-LR** | 41/53 (77.4%) — **tied** | 140/220 (63.6%) | **181/273 (66.3%)** |

Net gain applying the fitted weights to every case: **+3** (4 cases flipped
wrong→correct: L1 c94, L4 c35, L9 c22, L9 c32; 1 flipped correct→wrong: L4 c42).

**Does more training data help?** Refit on **100% of the data** (all 273 cases,
no held-out split) and re-evaluate on all 273 cases:

| | 80/20-fit → all cases | 100%-fit → all cases |
|---|---|---|
| L1 | 79/99 (79.8%) | 79/99 (79.8%) |
| L4 | 34/77 (44.2%) | 34/77 (44.2%) |
| L9 | 68/97 (70.1%) | 68/97 (70.1%) |
| **Total** | **181/273 (66.3%)** | **181/273 (66.3%)** |

**Identical outcome on every single case.** This is not a sample-size-limited
problem — adding the extra 53 cases to the fit doesn't change a single decision.

---

## 7. Why is accuracy capped around 65-66% overall? Root-cause breakdown

Every case falls into exactly one of three buckets, and **only one of them is
something a scoring-weight change can ever affect**:

| Length | `no_correct_available`<br>(MCTS never generated *any* correct script — unfixable by scoring) | `all_correct`<br>(every candidate is correct — already fine regardless of weights) | `mixed_competitive`<br>(correct **and** wrong both exist — the only bucket where weights matter) |
|---|---|---|---|
| L1 (99) | 7 | 24 | 68 |
| L4 (77) | **41 (53%)** | 5 | 31 |
| L9 (97) | 26 | 7 | 64 |

**L4's 44.2% overall accuracy is fundamentally a search/candidate-generation
problem, not a scoring problem**: 53% of L4 cases never had a correct script
appear anywhere in the entire MCTS log, across every iteration and every
critique. No weight vector can select a correct script that was never generated.
The theoretical ceiling for L4 is `(5 + 31)/77 = 46.8%`, and the fitted weights
already reach `34/77 = 44.2%` — within 2 cases of that ceiling.

**Restricting to just `mixed_competitive` cases** (the only ones where
reweighting is even possible) tells the real story:

| Length | Equal-weight | Pairwise-LR (100% fit) | Δ |
|---|---|---|---|
| L1 | 54/68 (79.4%) | 55/68 (80.9%) | +1 |
| L4 | 29/31 (93.5%) | 29/31 (93.5%) | 0 |
| L9 | 59/64 (92.2%) | 61/64 (95.3%) | +2 |

Within its actual reach, the scoring function already does quite well (79-95%),
and the learned weights add a modest further improvement, concentrated on L9.

**Is some of the remaining gap mathematically unfixable?** Checked whether, within
each `mixed_competitive` case, some wrong script's 4 components weakly dominate
(`≥` in every one of the 4 dimensions) every correct script's components — if so,
**no** nonnegative weight vector could ever rank that correct script on top,
regardless of fitting method:

| Length | Unfixable / mixed cases |
|---|---|
| L1 | 10/68 (14.7%) |
| L4 | 1/31 (3.2%) |
| L9 | 1/64 (1.6%) |
| **Total** | **12/163 (7.4%)** |

Only a small slice (7.4%) is truly unfixable by *any* linear weighting — most of
the remaining L1 gap (79.4%→ceiling ~100%) is in principle closeable by a better
weight vector or a richer (non-linear / additional-feature) scoring function.

---

## 8. Evaluation methodology (applies to all methods above)

- **Case split:** 80/20, stratified by length, shuffled with fixed `seed=42`
  (`split_cases` in both fitting scripts) — held-out cases are entire *cases*,
  never individual scripts, since scripts from the same case are correlated
  (they share the same ground truth and often similar structure).
- **Metric:** `accuracy(w)` as defined in §1 — fraction of cases where
  `argmax_s w·x(s)` is a correct script — computed separately on held-out cases,
  in-sample train cases, and (for the 100%-fit experiment) all cases combined.
- **Baseline:** the current hardcoded equal-weight formula (`w=[0.25]*4`),
  included in every comparison table.

---

## 9. Files

| File | Purpose |
|---|---|
| `build_score_regression_dataset.py` | Extracts every unique script per case from the MCTS logs, runs TRAIN + TEST variants, recomputes score components + correctness. Produces `score_regression_dataset.csv`. |
| `score_regression_dataset.csv` | 1,192 rows (1,077 after cleaning) — one row per (case, unique script). |
| `fit_score_weights_lp.py` | Method A: LP regression of weighted score onto `partial_reward` (LAD/L1 loss). **Not recommended** — degenerate weights, worse than baseline on the real metric. |
| `fit_score_weights_regression.py` | Methods B & C: pointwise and pairwise logistic regression, plus the held-out/in-sample evaluation harness. **Pairwise-LR is the best method found so far.** |

**Reproduce everything:**
```bash
cd ~/transchema && source env/bin/activate
python3 build_score_regression_dataset.py --workers 30   # ~15-25 min, only needed once
python3 fit_score_weights_lp.py
python3 fit_score_weights_regression.py
```

---

## 10. Bottom line

- The **pairwise ranking logistic regression** is the recommended weight vector
  so far: `fd_f1=0.124, avg_col_score_1=0.249, row_count_score=0.356,
  max_missing_score=0.271` (normalized), giving a modest but genuine **+3 cases**
  over equal weights (181/273 vs 178/273), concentrated in L9.
- The **LP-regress-to-partial_reward** approach should be discarded — it
  optimizes a metric (`partial_reward` gap) that doesn't track true correctness
  and actively makes case-level accuracy worse.
- **More data does not help** — fitting on 100% vs 80% of cases gives identical
  decisions on every case, so this isn't a sample-size problem.
- The real ceiling on overall accuracy, especially for L4 (44.2%) and L9 (68-70%),
  is set by **how many cases MCTS ever generates a correct script for at all**
  (53% failure for L4, 27% for L9) — a search/generation-coverage issue, not a
  scoring-weight issue. Within the subset of cases where scoring can actually
  matter, the function already performs at 79-95%, with only ~7% of that
  remaining gap being mathematically unfixable by any linear reweighting.
- **Suggested next step:** investigate why MCTS fails to generate any correct
  script for such a large fraction of L4/L9 cases — that's the higher-leverage
  lever left, not further weight tuning.
