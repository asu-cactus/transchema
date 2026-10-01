# Ablation Study Results — Compiled So Far

All rows: `dmx-gpt-oss-120b`, `--reward det_score_value`, `--data_split training`, GitHub-pipelines
(698 case folders, /700 convention: missing/unrun cases count as incorrect) and Smart Building v2
(105-case benchmark). Compiled 2026-09-28 from `logs_langraph/ablation_*_batch.log` on this machine
(`en4175917l`). Rows marked **PENDING** are running or awaiting compilation on a different server —
I have no SSH access to either remote box this session, so those numbers are not in this file yet.

**Pass pattern varies by ablation** (noted per table) — do not compare a single-pass row directly
against a 2-phase row without accounting for that.

---

## 0. Baseline (production defaults, for reference)

λ=0.5, τ=1.0 (strictest — critique fires whenever score < 1.0), RAG=curated_pipeline
(prefix_feature retrieval), full reward (no dropped components).

| Benchmark | Leaf-stop only (phase 1) | 2-phase (+ no-leafstop retry) |
|---|---|---|
| GitHub (/700) | 466/700 = 66.6% | 517/700 = 73.9% |
| Smart Building (/105) | 54/105 = 51.4% | 64/105 = 61.0% |

Source: `RESULTS_github_oss120b.txt`, `RESULTS_sb105_mcts_vs_baselines.txt`.

---

## 1. Reward-function ablation (drop one `score_1` component)

**Settings**

| Setting | Value |
|---|---|
| Flag | `--drop_score_components <name>` |
| Pass pattern | Single pass, `same_leaf_stopping=0` (no leaf-stop, no retry phase) |
| Redundancy | 2 runs per stage, OOM-recovery only (re-catches kernel-killed cases with no result — not a genuine 2nd attempt) |
| GitHub cases | 680/698 (excludes length-4 0–17, known memory-heavy) |
| Smart Building cases | 105/105 |
| Server | This machine (`s_fd`, `s_col`) / 10.218.105.162 (`s_rows`+`s_missing`, `s_cred`) |
| Script | `run_ablation_reward_wofd_wocol.sh` / `run_ablation_reward_rowsmissing_wocred.sh` |

**Results**

| Config | GitHub (as-run) | GitHub /700-equiv* | Smart Building /105 |
|---|---|---|---|
| w/o `s_fd` (fd_f1) | 490/680 = 72.1% | 490/700 = 70.0% | 54/105 = 51.4% |
| w/o `s_col` (avg_col_score_1) | 461/680 = 67.8% | 461/700 = 65.9% | 56/105 = 53.3% |

**Oracle** (did the MCTS *search* ever generate a correct pipeline for the case, independent of
whether the possibly-ablated reward function selected it as best? See `oracle_validate.py`.)

| Config | GitHub Oracle | Smart Building Oracle |
|---|---|---|
| w/o `s_fd` | 548/694 = 79.0% | 67/105 = 63.8% |
| w/o `s_col` | 528/680 = 77.6% | 68/105 = 64.8% |

The Oracle-vs-selected gap (e.g. GH w/o s_fd: 79.0% generated correct vs. 72.1% actually
selected) is the ablated reward's *selection* loss — cases the search found a correct answer
for but the degraded scorer failed to pick out as best.
| w/o `s_rows`+`s_missing` | **PENDING** (10.218.105.162) | — | — |
| w/o `s_cred` | **PENDING** (10.218.105.162) | — | — |

\* treats the 18 never-run L4 cases as incorrect, matching the project's /700 convention.

Log: `logs_langraph/ablation_wofd_wocol_batch.log`.

---

## 2. Retrieval ablation

### 2a. No RAG at all (baseline for the family)

**Settings**

| Setting | Value |
|---|---|
| Flag | `RAG=""` (empty — `${RAG-curated_pipeline}` default semantics keep it disabled) |
| Pass pattern | Single pass, `same_leaf_stopping=5` (launcher default), no retry phase |
| Cases | GitHub 698/698, Smart Building 105/105 |
| Server | This machine |
| Script | `run_ablation_no_rag.sh` |

**Results**

| Benchmark | Result |
|---|---|
| GitHub (/700) | 474/698 = 67.9% (/700: 67.7%) |
| Smart Building (/105) | 55/105 = 52.4% |

Log: `logs_langraph/ablation_no_rag_batch.log`.

### 2b. RAG retrieval-strategy sweep (within `--rag curated_pipeline`, 656-pipeline corpus)

**Settings**

| Setting | Value |
|---|---|
| Flag | `--curated_retrieval_mode <mode>` (new; default `prefix_feature` = unchanged prior behavior) |
| Pass pattern | 2-phase (leafstop 5, then no-leafstop retry of phase-1 failures) |
| Cases | GitHub 698/698, Smart Building 105/105 (104/105 for `prefix_embedding`, see below) |
| Server | This machine (`embedding_only`, `prefix_embedding`) / 10.218.105.162 (`feature_only`, `prefix_only`) |
| Script | `run_ablation_rag_embedding.sh` / `run_ablation_rag_prefix.sh` |

**Results**

| `--curated_retrieval_mode` | GitHub (/698, 2-phase) | GitHub /700-equiv | Smart Building |
|---|---|---|---|
| `prefix_feature` (= production default/baseline) | 517/700 | 73.9% | 64/105 = 61.0% |
| `embedding_only` (no prefix filter, rank by text-embedding cosine sim) | 526/698 = 75.4% | 75.1% | 64/105 = 61.0% |
| `prefix_embedding` (prefix-match, rank by text-embedding cosine sim) | 536/698 = 76.8% | 76.5% | 63/104† = 60.6% |
| `feature_only` (no prefix filter, rank by 8-dim structural feature cosine sim) | **PENDING** (10.218.105.162) | — | — |
| `prefix_only` (prefix-match, then random pick — no similarity ranking) | **PENDING** (10.218.105.162) | — | — |

† Smart Building `prefix_embedding` phase 2 only recovered a result for 104/105 cases — one case
produced no result in either phase; not yet root-caused.

Log: `logs_langraph/ablation_rag_embedding_batch.log` (this machine) /
`logs_langraph/ablation_rag_prefix_batch.log` (105.162).

---

## 3. Expansion-policy ablation (λ mixing weight: S = λ·S_LLM + (1−λ)·S_rule)

**Settings**

| Setting | Value |
|---|---|
| Flag | `TREEMORPHER_EXPAND_LAMBDA=<value>` env var (`Langraph/nodes.py` `_OPERATOR_CONFIG_LAMBDA`) |
| Pass pattern | 2-phase (leafstop 5, then no-leafstop retry of phase-1 failures) |
| Cases | GitHub 698/698, Smart Building 105/105 |
| Server | This machine (λ=0.25, 0.75) / 10.218.106.238 (λ=0, 1) |
| Script | `run_ablation_lambda_sweep.sh` / `run_ablation_lambda01_sweep.sh` |

**Results**

| λ | GitHub (/698, 2-phase) | GitHub /700-equiv | Smart Building |
|---|---|---|---|
| 0.0 | **PENDING** (10.218.106.238) | — | — |
| 0.25 | 531/698 = 76.1% | 75.9% | 62/105 = 59.0% |
| 0.5 (baseline) | 517/700 | 73.9% | 64/105 = 61.0% |
| 0.75 | 532/698 = 76.2% | 76.0% | 66/105 = 62.9% |
| 1.0 | **PENDING** (10.218.106.238) | — | — |

Log: `logs_langraph/ablation_lambda_sweep_batch.log` (this machine).

Note (D10 in `ABLATION_PLAN_README.md`): λ=0 does not mean "pure statistics" — the LLM still
proposes operator *types*; only JOIN/GROUP_BY/AGGREGATE have a real rule engine, so other operator
types (UNION/PIVOT/UNPIVOT/COLUMN_TRANSFORM) tie at S=0.0 and break ties via unordered `set`
iteration at λ=0 — a known methodological gap, not yet fixed (deferred, pending a decision).

---

## 4. Critique-invocation-threshold ablation (τ)

**Settings**

| Setting | Value |
|---|---|
| Flag | `TREEMORPHER_CRITIQUE_THRESHOLD=<value>` env var (`Langraph/nodes.py` `should_critique()`) / `MCTS_CRITIQUE_MODE=none` for no-critique |
| Pass pattern | 2-phase (leafstop 5, then no-leafstop retry of phase-1 failures) |
| Cases | GitHub 698/698, Smart Building 105/105 |
| Server | 10.218.106.238 (all 4 configs) |
| Script | `run_ablation_critique_threshold.sh` (run manually there, not via my watchdog) |

**Results**

| τ | GitHub | Smart Building |
|---|---|---|
| 0.7 | **PENDING** (10.218.106.238) | — |
| 0.8 | **PENDING** (10.218.106.238) | — |
| 0.9 | **PENDING** (10.218.106.238) | — |
| 1.0 (baseline, strictest — default for `det_score_value`) | 517/700 = 73.9% | 64/105 = 61.0% |
| no critique (`--mcts_critique_mode none`) | **PENDING** (10.218.106.238) | — |

Log (once available there): `logs_langraph/ablation_critique_threshold_batch.log`.

---

## 5. Reward-function-FAMILY ablation (swap the whole reward, not one component)

Distinct from §1 (which drops one `score_1` component at a time from `det_score_value`) — this
swaps TreeMorpher's entire reward function for a competing method's own reward formulation.
See `Langraph/nodes.py`'s `_score_and_validate_output` and commit `51f6a1bd` for the exact
formulas (`bat_reward`: BAT's column-name overlap ratio, no target values read; `ap_reward`:
Auto-Pipeline-style FD-overlap + key-overlap + column-mapping mean, `[0,1]`; `llm_confidence`:
critique's self-reported blended confidence used directly as the reward).

**Settings**

| Setting | Value |
|---|---|
| Flag | `--reward {bat_reward,ap_reward,llm_confidence}` |
| Pass pattern | Single pass, `same_leaf_stopping=0` (no leaf-stop, no retry phase), `TREEMORPHER_CRITIQUE_THRESHOLD=0.8` uniformly |
| Cases | GitHub 698/698 (695-698 produced a result depending on mode), Smart Building 105/105 |
| Server | This machine (all 3 modes) |
| Script | `run_ablation_reward_family.sh` |

**Results**

| Config | GitHub (/700) | Smart Building (/105) |
|---|---|---|
| `bat_reward` | 301/700 = 43.0% | 48/105 = 45.7% |
| `ap_reward` | 402/700 = 57.4% | 48/105 = 45.7% |
| `llm_confidence` | 374/700 = 53.4% | 52/105 = 49.5% |

Compare to baseline (§0): `det_score_value` gets 517/700 = 73.9% GH / 64/105 = 61.0% SB — all
three alternate reward formulations land well below it as standalone MCTS reward signals.

**Oracle** (did the search ever generate a correct pipeline, independent of which candidate the
reward function actually selected as best?)

| Config | GitHub Oracle | Smart Building Oracle |
|---|---|---|
| `bat_reward` | 252/698 = 36.1% | 48/105 = 45.7% |
| `ap_reward` | 390/698 = 55.9% | 54/105 = 51.4% |
| `llm_confidence` | 399/698 = 57.2% | 58/105 = 55.2% |

Log: `logs_langraph/ablation_reward_family_batch.log`. Oracle CSVs: `*_oracle.csv` at repo root
(`oracle_validate.py --exp_name github_abl_rewfam_{bat,ap,conf}_{gh,sb}_dmx-gpt-oss-120b`).

**Known undercount for `ap_reward`/`llm_confidence` GitHub Oracle**: both read slightly *below*
their own selected accuracy (ap_reward: 390/698=55.9% Oracle vs 402/700=57.4% selected;
llm_confidence similarly) — logically Oracle should never be below selected accuracy, since the
selected script is itself one of the candidates. Root-caused: `oracle_validate.py` only extracts
scripts from the normal per-iteration simulate/critique logging (`[simulate/pipeline] Trial N:`
and `$END_CONFIDENCE$`-anchored blocks); a case that hits the 600s case_timeout gets its winning
script from a separate checkpoint-recovery path (`status=timeout_recovered` in
results_summary.csv) that Oracle's extraction doesn't cover. Confirmed on case `1_19`
(`ap_reward`, `status=timeout_recovered`) — selected-correct, but no matching script in Oracle's
extracted candidates. Timeout-recovered case counts vary sharply by reward mode (weaker/noisier
rewards converge slower): `bat_reward` 2/698 (negligible), `ap_reward` 78/698, `llm_confidence`
180/698 — so `bat_reward`'s Oracle number is reliable, `ap_reward`'s is a mild undercount, and
`llm_confidence`'s GitHub Oracle (57.2%) should be read as a likely-meaningful undercount of the
true value. Not fixed here (would need extracting the checkpoint-recovered script separately,
e.g. from the `python_recovered*.py` files written alongside each case) -- flagged as a known
gap rather than silently trusted.

---

## 6. No-static-hints and weight-tuning ablations (set up, not yet run)

Both built and verified (dry-run + live single-case tests) on this machine, handed off to run
on a different server as a chained queue (`run_ablation_no_static_hints.sh` then
`run_ablation_equal_weights.sh`, via `watchdog_ablation_queue.sh`). See commits `302e8624`
(the `--no_static_hints` expand-step bug fix this depended on) through `ad007c21`.

| Ablation | Flag(s) | Pass pattern | Server |
|---|---|---|---|
| No static hints | `NO_STATIC_HINTS=1` (RAG stays on) | Two-phase | Other server (not yet confirmed launched) |
| Weight tuning ("equal") | `SCORE_WEIGHTS=equal` (top-level + nested column-type weights both uniform) | Two-phase | Other server (not yet confirmed launched) |

---

## Still to compile / verify

| # | Item | Server | Status |
|---|---|---|---|
| 1 | Reward: w/o s_rows+s_missing, w/o s_cred | 10.218.105.162 | Pending — pull `logs_langraph/ablation_reward_rowsmissing_wocred_batch.log` |
| 2 | RAG strategy: feature_only, prefix_only | 10.218.105.162 | Pending — pull `logs_langraph/ablation_rag_prefix_batch.log` |
| 3 | Expansion λ=0, λ=1 | 10.218.106.238 | Pending — pull `logs_langraph/ablation_lambda01_sweep_batch.log` |
| 4 | Critique τ=0.9/0.8/0.7, no-critique | 10.218.106.238 | Pending — pull `logs_langraph/ablation_critique_threshold_batch.log` |
| 5 | Root-cause the 104/105 case in SB `prefix_embedding` | This machine | Not investigated yet |
| 6 | No-static-hints | Other server | Set up, launch not confirmed |
| 7 | Weight tuning (equal) | Other server | Set up, launch not confirmed |
| 8 | Ablation Plan §6 (search budget) | — | Not started |
| 9 | Oracle extraction misses timeout-recovered cases' scripts (§5 note) | This machine | Root-caused; not fixed -- extend `oracle_validate.py` to also extract `python_recovered*.py` if these numbers end up load-bearing |
