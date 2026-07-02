# Run 9: `best_score_script_mcts` branch — analysis notes

Branch: `best_score_script_mcts` (off `mcts_utility_branch`).
Goal: fix the MCTS reward/selection pipeline so the search reliably picks a
genuinely correct script, starting from run8's `det_score_value` reward
(`max(score_1, score_2)`) and run8's `extract_best()` (accumulated
`total_reward` greedy path).

## Baseline numbers (L1, 100 cases, before this branch)

| Experiment | Correct |
|---|---|
| run7 | 73/100 |
| run8 Method A (global best training score, offline replay) | 74/100 |
| rag_global_redo | 93/100 |

## Code changes made on this branch

1. **`eval_score_value_based.py` — `score_1` formula**
   - Added `row_count_score` (`min(len(gen), len(gt)) / max(...)`, on *total*
     row count) and `max_missing_score` (`1 - |max_col_missing_frac(gen) -
     max_col_missing_frac(gt)|`) as two new components. The existing
     `row_ratio` (used in `score_2`) discounts rows with any missing value
     *before* comparing counts, so it's blind to total row-count blowups
     (e.g. a reversed merge direction that keeps the wrong/larger source
     table). These two new components catch that.
   - `score_1 = (fd_f1 + avg_col_score_1 + row_count_score +
     max_missing_score) / 4`, where the numeric-column contribution to
     `avg_col_score_1` changed from `range_overlap` alone to
     `min(range_overlap, js_similarity)` — a pessimistic ("AND") ensemble.
     `range_overlap` alone can be fooled by envelope-matching tricks (e.g.
     `(min+max)/2` compresses toward GT's endpoints without matching its
     true distribution); JS similarity catches that even when range_overlap
     doesn't, so `min()` lets JS veto a range_overlap false positive.
   - `true_combined_score = score_1` (was `max(score_1, score_2)`). The
     `max()` was an escape hatch: even after `score_1` was fixed, a
     row-count-inflating script could still win via the untouched
     `score_2`/`row_ratio`. Dropping the dual-score max removes that.
   - `build_jaccard_column_map()`: categorical and ID-named (`"id" in
     col.lower()`) GT columns now match a same-named gen column by exact
     name first, falling back to the old fuzzy value-based search only when
     no exact name exists. Numeric (non-ID) columns are untouched — still
     value-based, since those are legitimately renamed with `_x`/`_y`
     suffixes. Reason: the fuzzy matcher is a small-sample-noisy heuristic
     that can confidently mismatch two unrelated columns (categorical or
     small-range-integer ID columns look statistically similar to each
     other) — see case 14 and case 5 below.

2. **`Langraph/nodes.py` — `extract_best()`**
   - Now returns the GLOBAL best-scoring script seen anywhere during search
     (`state["best_score"]`/`state["best_script"]`, already tracked
     incrementally by `execute_and_score()` and `mcts_critique()`), instead
     of walking `root.best_reward_path()` (greedy descent by accumulated
     `total_reward`) and taking that leaf's locally-cached script. Tree
     exploration (UCB1 selection, dual-pass critique backprop) is
     unchanged — only which script gets extracted as the final answer
     changed.
   - **This is superseded by later findings below (global best score is not
     the best strategy) — see "Selection strategy comparison."**

3. **`Langraph/mcts_search.py`**
   - The per-graph-step checkpoint used for timeout/OOM recovery
     (`/tmp/mcts_checkpoint_*.json`) was hardcoded to
     `root.best_reward_path()[-1]` — the OLD accumulated-reward leaf, not
     the new global best. Fixed to pull from `state["best_score"]`/
     `["best_script"]` so timeout/OOM recovery is consistent with normal
     completion.
   - `_CASE_TIMEOUT`: `300` → `600` (5 min → 10 min per case).

4. **`hints/hints_static.py`**
   - Hint #22 (average aggregation) strengthened: was a soft "always use
     the simple mean... NEVER approximate as (min+max)/2... NEVER use a
     weighted average"; now uses explicit "MUST"/"STRICTLY FORBIDDEN"
     language and includes the exact violating pattern observed in case 3
     (`(df['Median'] * df['Total']).sum() / df['Total'].sum()`) as a named
     counter-example.
   - New hint #36: "NEVER join using left_index=True/right_index=True. If
     a named key/ID column exists, join on it directly by name." — added
     after diagnosing case 5 (see below). Registered in `JOIN_HINT_IDS`,
     `PYTHON_SCRIPT_HINT_IDS`, `CRITIQUE_HINT_IDS`, `PIPELINE_HINT_IDS`
     (same groups as hint #35, its closest sibling).

5. **`prompts/mcts_simulate.py`**
   - Simulate prompt's "reason about additional steps" instruction now
     explicitly tells the model to add `NO_MORE_OPERATION` if no more steps
     are needed, instead of leaving that implicit.

## Specific bugs diagnosed (each with a concrete case as evidence)

| Case | Bug | Root cause |
|---|---|---|
| 14 | Categorical column Jaccard mismatch | On small tables (9 rows), value-based column matching scrambled numeric columns (`FGM`→`PPG`, etc.) with high confidence, corrupting every downstream metric. Fixed for categorical/ID columns via exact-name matching; **numeric columns are still exposed** (case 14 itself is a numeric-column instance, unfixed). |
| 25, 33, 45, 63, 73, 79 | Outer-vs-inner join row inflation | `row_ratio` discounts incomplete rows before comparing counts, so a script that keeps a larger/wrong source table via `how="outer"` isn't penalized for the row-count blowup. Fixed by `row_count_score`/`max_missing_score`. |
| 4 | Self-union trick (`pd.concat([df0, df0])`) | Doubles row *values* without changing row *count* (same number of groups). Fools JS-similarity too, not just range_overlap — **unfixed**, since the training partition's true scale differs from `target.csv`'s scale, and the trick coincidentally lands closer to GT's magnitude. |
| 0 | `(min+max)/2` instead of `.mean()` | Compresses toward GT's min/max endpoints, fooling `range_overlap` even though the true `.mean()` is closer to GT's actual mean. Fixed by `min(js, range_overlap)` in `score_1`. |
| 3, 6 | Weighted average (`sum(value*weight)/sum(weight)`) | Same mechanism as case 0, but here JS *itself* is also fooled (not just range_overlap) because the weighting genuinely compensates for a training/target sampling skew. **Unfixed** by the scoring formula — addressed via hint #22 strengthening instead (untested as of this writing — the pilot run predates the hint change). |
| 5 | `right_index=True` join bug | `pd.read_csv(..., index_col=0)` silently consumes an anonymous `Unnamed: 0` row-counter column into the DataFrame index; joining on `right_index=True` uses that meaningless index instead of the real named ID column. Off-by-one, nearly invisible in aggregate stats (`nunique_sim` etc. don't see it). Root cause was ALSO an ID-column Jaccard mismatch (`ProvinciaID`↔`RegionID` confused) that made the true and buggy scripts score nearly identically even before the join bug's effect showed up. Fixed via ID-column exact-name matching (`eval_score_value_based.py`) + hint #36. |
| 10 | Party-vote undercounting bug | Pivot-then-resum implementation silently dropped a party category not included in the final resum list, undercounting — but the undercounted total happened to land closer to GT's (smaller) true scale than the correct full total. Same "train/target scale mismatch" root cause as case 4. |
| 17 | Small (7-row) join row inflation | `row_count_score` correctly detects the 7/19585-row gap, but the margin is too thin (0.9996 vs 1.0) to overcome `fd_f1`'s bias toward more rows (FD mining favors larger tables almost regardless of correctness — a **second, distinct** scoring vulnerability from the row-count one). |

## Experiments run on this branch

- `run_rag_det_score_run9_l1_pilot20.sh` — cases 0-19, `--max_depth 2`,
  `--mcts_iterations 40`, `MAX_JOBS=20`. Final result: **15/20** (wrong:
  3, 4, 6, 8, 10 — after the categorical/ID-matching and hint fixes;
  earlier pilot runs before those fixes had different wrong sets).
- `run_rag_det_score_run9_l1_batch.sh 20 99` (batch runner, takes
  `START END` args) — cases 20-99. Result: **63/80**.
- **Full L1 total: 78/100** (vs. run7's 73, run8's 74, redo's 93).

## Selection strategy comparison (offline, replaying the run9 trees — no re-running MCTS)

Reconstructed each of the 100 cases' MCTS trees from their logs and tested
4 different final-answer-selection strategies against the SAME trees:

| Strategy | Correct (/100) | Mechanism |
|---|---|---|
| `BEST_SCORE` (current `extract_best()`) | 78 | Global max score anywhere in the search |
| `OLD_total_reward` (pre-branch `extract_best()`) | 79 | Greedy descent by accumulated `total_reward`, always walks to an actual leaf |
| `Q_VALUE` | 78 | Greedy descent by `total_reward/visits` (average reward) |
| `LCB_C=0.5` (on tree path) | 79 | Greedy descent by `q_value - 0.5/sqrt(visits)` |
| **Flat hybrid `C=0.1`** | **84** | No tree-walking: argmax over *every* distinct script ever scored in the log, ranked by `score - 0.1/sqrt(freq)` where `freq` = how many iterations produced that exact score |

Key findings from this comparison:
- **`BEST_SCORE`/`Q_VALUE` are exploitable by single-visit flukes.** Cases 4
  and 6 (self-union, weighted-average) are won by nodes with only 1-3
  visits/frequency, while the correct script has 3-16x more supporting
  visits at a slightly lower score. No confidence discount for sample size.
- **`OLD_total_reward`/`LCB` have a structural "leaf-forcing" bug.** Cases
  9, 16, 18: the true best-scoring script is at a *shallow* node
  (`GROUP_BY` with no `AGGREGATE` needed, or even the root — no operation
  at all), but the greedy walk is a `while node.children:` loop with no
  stopping condition other than reaching an actual leaf, so it's forced
  past the correct shallow answer into a worse, deeper sibling.
  Q_VALUE (vs. total_reward) fixes this specific pattern by normalizing
  for visit count, but is still vulnerable to the single-visit-fluke issue.
- **The flat hybrid avoids the leaf-forcing bug entirely** (no tree walk,
  so no forced descent) while still applying a confidence discount (so
  single-visit flukes lose to well-supported alternatives).
- **Flat hybrid's remaining failure mode**: when the *correct* script
  itself is rare (freq=1-3) — not because it's wrong, but because it's a
  less obvious pipeline the LLM stumbles into less often — the confidence
  penalty demotes it too. Cases 54, 75, 95 regressed for exactly this
  reason. A pure frequency-based confidence signal can't distinguish
  "rare because it's an exploit" from "rare because it's a less common
  correct answer."
- **12 cases are wrong under every strategy tested**: `22, 24, 44, 64, 85,
  86, 88, 89, 90, 93, 96, 99`. Several have no correct script anywhere in
  the log at all (a generation problem, not a selection problem); one
  (`89`) has a genuine script execution error, not a logic bug.

**Status: the flat hybrid (`C=0.1`) is the best strategy found so far but
is NOT yet wired into `extract_best()`** — `Langraph/nodes.py` still uses
the plain global-best-score approach. This is the natural next step.

## Analysis scripts (all on this branch, not run7/run8's original code)

- `analyze_run8_failed_case_scripts.py` — extracts every unique script from
  a case's MCTS log with scores, evaluates each against TEST data, reports
  the chosen (highest-scoring) vs. best-correct script and how many times
  each score/script recurred in the log. Core building block reused by
  most other scripts below.
- `analyze_run8_regression_check.py` — for a set of cases, re-scores every
  unique script in the log with the CURRENT (patched) `score_1` and checks
  whether the new highest-scoring pick is still correct (used to validate
  that fixes to `score_1` don't regress previously-correct cases).
- `analyze_run9_reward_path_vs_maxscore.py` — reconstructs trees from run9
  pilot logs and compares `OLD_total_reward` vs `NEW` (global best score)
  selection on the same trees.
- `analyze_run9_min_visits_lcb.py` — tests `min_visits` threshold and LCB
  variants of the greedy tree-path walk against the pilot's 20 cases.
- `analyze_run9_full100_path_comparison.py` — same comparison
  (`OLD_total_reward` / `Q_VALUE` / `LCB_C=0.5`) extended to all 100 cases,
  parallelized with `ProcessPoolExecutor`.
- `analyze_run9_wrong_cases_scores.py` — for the union of cases wrong under
  any selection strategy, reports the live-chosen score vs. the
  best-correct score found in the log.
- `analyze_run9_unique_score_analysis.py` — per-case, per-method: chosen
  score, its rank among all scores in the log, how many times that exact
  score recurred, and the tree node's visit count (fast — no script
  execution, pure log/tree parsing).
- `analyze_run9_hybrid_full100.py` — implements and validates the flat
  LCB-style hybrid selection rule (`score - C/sqrt(freq)`, argmax over all
  distinct scripts in the log, no tree-walking) against all 100 cases.

## Run scripts

- `run_rag_det_score_run9_l1_pilot20.sh` — cases 0-19 pilot.
- `run_rag_det_score_run9_l1_batch.sh START END` — generalized batch
  runner for the remaining case ranges (used for 20-99).

## Open items / natural next steps

1. Wire the flat hybrid (`C=0.1`) selection into `extract_best()` in place
   of the current global-best-score logic, then re-run the full 100 cases
   live to confirm the offline replay numbers hold up (live search
   dynamics can differ from replaying already-completed logs).
2. Cases 3/6's weighted-average fix (hint #22 strengthening) hasn't been
   validated in a live run yet — the pilot predates that change.
3. The self-union exploit (case 4) and the FD-mining row-count bias (case
   17) remain unaddressed by any scoring-formula fix so far; both are
   train/target-partition-scale-mismatch artifacts that may need a
   different approach (e.g. a partition-aware scoring adjustment, or
   accepting them as inherent limits of value-distribution-based scoring
   without exact-match ground truth during training).
4. 12 cases fail under every method tried — worth a dedicated pass to
   determine how many are genuine "no correct script ever generated"
   (prompt/generation issue) vs. scoring issues we haven't found yet.
