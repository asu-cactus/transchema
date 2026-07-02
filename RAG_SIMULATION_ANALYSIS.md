# MCTS Simulation RAG Hit-Rate Analysis (a4 upper-bound vs. global embedding RAG)

Analysis of **why the pipeline-simulate RAG hit-rate is low** in the two-tier RAG MCTS
experiments, and what it costs in accuracy. Two experiments compared:

- **a4 (`upper_bound`)** — local RAG DB holds exactly **one** pipeline per case: that
  case's own ground truth. Scripts: `run_mcts_l149_pipeline_a4.sh`, `run_mcts_l2356_pipeline_a4.sh`.
- **global** — local RAG DB is populated with the **top-50 schema-similar** pipelines
  retrieved from a 12,264-example embedding store. Scripts: `run_mcts_l149_rag_global_partial.sh`,
  `run_mcts_l2356_rag_global_partial.sh`.

A pipeline-simulate RAG call **hits** iff some stored pipeline satisfies
`stored_abstract[:depth] == rollout_abstract_prefix  AND  len(stored) > depth`,
where operators are binned: `JOIN→merge`, `GROUP_BY/AGGREGATE→groupby`, `UNION→union`,
`PIVOT→pivot`, `UNPIVOT→unpivot`, `NO_MORE_OPERATION→terminal`.

> Data sources: per-case `[simulate] Iter …` / `RAG hints retrieved …` lines in
> `logs_langraph/mcts_l*_p*_rag_*_pipeline/*.log`; correctness from
> `Langraph/results_langraph/<experiment>/results_summary.csv`; ground truth from
> `ground_truth_pipelines.csv`; global store in `rag_pipeline/db/global_schema.*`.

---

## 1. Simulate hit-rate by pipeline length

| Length | a4 calls | a4 hits | a4 % | global calls | global hits | global % |
|--------|---------|---------|------|--------------|-------------|----------|
| L1 | 342  | 82  | 24.0% | 404  | 82  | 20.3% |
| L2 | 503  | 73  | 14.5% | 504  | 99  | 19.6% |
| L3 | 592  | 138 | 23.3% | 755  | 126 | 16.7% |
| L4 | 955  | 101 | 10.6% | 875  | 68  | 7.8%  |
| L5 | 1094 | 381 | 34.8% | 1193 | 352 | 29.5% |
| L6 | 343  | 145 | 42.3% | 358  | 94  | 26.3% |
| L9 | 453  | 100 | 22.1% | 433  | 50  | 11.5% |
| **Total** | **4282** | **1020** | **23.8%** | **4522** | **871** | **19.3%** |

(Hit-rate counted only on the pipeline-simulate call; expand/critique phases excluded.)

---

## 2. a4 — why low *despite* a guaranteed match

Since the a4 store is the single GT pipeline, every miss is exactly one bucket.
Script: `analyze_a4_sim_misses.py`.

| Bucket | Count | Share of misses | Meaning |
|--------|------:|----------------:|---------|
| **divergent** | 2766 | **84.8%** | rollout path is NOT a prefix of the GT path (wrong branch / order / granularity) |
| exhausted | 406 | 12.4% | rollout already at/past full GT length — nothing left to suggest |
| no-structural-GT | 90 | 2.8% | GT has no structural ops (`split`, `Date`) — RAG can't help by construction |

- **Hypothesis (a) — MCTS exploring a different branch — confirmed dominant (85%).**
- **Hypothesis (b) — operator standardization — NOT a factor at the bin level** (0 unbinnable
  ops; binning is consistent on both sides). Granularity/order mismatches are absorbed into
  "divergent" (see §4).
- Even at **depth 1**, MCTS picks the GT's first operator only **51.4%** of the time.

---

## 3. Global — why top-100 barely helps

Faithful replay: re-ran the embedding retrieval per case (top-100) and replayed each case's
actual rollout histories against the top-50 and top-100 candidate sets.
Script: `analyze_global_sim_misses.py`. Replay@50 = 20.5% reproduces the observed 19.3%.

| Length | calls | hit@50 | %@50 | hit@100 | %@100 | Δ pts |
|--------|------:|-------:|-----:|--------:|------:|------:|
| L1 | 404  | 79  | 19.6% | 81  | 20.0% | +0.5 |
| L2 | 504  | 102 | 20.2% | 102 | 20.2% | +0.0 |
| L3 | 755  | 139 | 18.4% | 144 | 19.1% | +0.7 |
| L4 | 875  | 92  | 10.5% | 97  | 11.1% | +0.6 |
| L5 | 1193 | 338 | 28.3% | 358 | 30.0% | +1.7 |
| L6 | 358  | 99  | 27.7% | 131 | 36.6% | **+8.9** |
| L9 | 433  | 80  | 18.5% | 96  | 22.2% | **+3.7** |
| **ALL** | **4522** | **929** | **20.5%** | **1009** | **22.3%** | **+1.8** |

**Decomposition of the 3,593 misses@50:**

| Share | Reason |
|------:|--------|
| 4.3%  | depth-1 rollout, first op absent from the 50 |
| 9.4%  | depth-1 rollout, first op present only as a non-extendable (complete) pipeline |
| 16.4% | depth≥2 rollout, first op already absent |
| **69.9%** | **depth≥2 rollout, first op present BUT the full operator sequence is absent** |

In **79%** of misses the correct first operator is already in the pool — the failure is that
the specific **multi-operator sequence** MCTS explores isn't present.

### Why top-100 doesn't help: the pool has low operator diversity

| Length | distinct shapes @50 | distinct @100 | NEW @100 | top-shape fills |
|--------|--------------------:|--------------:|---------:|----------------:|
| avg (all) | **5.8 / 50** | 8.1 / 100 | **+2.4** | **54.5%** |
| L5 | 4.4 | 7.4 | +3.1 | 71.0% |

A top-50 pool of 50 pipelines holds only **5.8 distinct operator shapes**; the single most
common shape fills **54%** of the pool. Doubling to 100 adds just **2.4 new distinct shapes** —
the extra 50 are mostly duplicates. The pool is flooded with simple shapes
(`merge>terminal`, `terminal`, `merge>groupby>terminal`, `groupby>terminal`).

➡ **The lever is pool *diversity*, not pool size** — operator-aware diversification
(dedupe / MMR by abstract shape) would beat sending 100 near-duplicates. L6/L9 (slightly more
diverse pools) were the only lengths to gain meaningfully at 100.

CSVs: `global_pool_diversity_by_len.csv`, `global_pool_shape_frequency.csv`,
`global_missing_sequence_patterns.csv`.

---

## 4. Divergence patterns — which pipelines hurt most (a4)

Script: `analyze_divergence_patterns.py`. CSVs: `a4_divergence_patterns.csv`,
`a4_divergence_by_gt_shape.csv`, `a4_divergence_by_rollout.csv`.

Top GT pipeline shapes by divergent misses:

| GT pipeline shape | div. misses | cases | div/case |
|---|---:|---:|---:|
| union>union>union>groupby>terminal | 399 | 28 | 14.2 |
| union>union>union>union>groupby>terminal | 295 | 16 | 18.4 |
| merge>groupby>terminal | 179 | 35 | 5.1 |
| merge>merge>merge>merge>groupby>terminal | 159 | 12 | 13.2 |

**The biggest culprit is multi-UNION (concat) pipelines.** The GT represents concatenating N
tables as **N separate `UNION` steps**, but MCTS rolls out a **single** `UNION` (or
`groupby>union`) — so the abstract sequences never align past depth 1. This is a
**granularity-standardization mismatch** (hypothesis b at the operator-count level, not the
bin-mapping level). Secondary clusters: operator **reordering** (`groupby↔merge`) and **early
stopping**.

---

## 5. Is it case-specific? — strongly bimodal

Script: `analyze_a4_per_case_missrate.py`. CSV: `a4_per_case_miss_rate.csv`.
Per-case miss-rate = (sim calls with no RAG hit) / (total sim calls), over 677 cases.

```
   0- 10% |  379  ██████████████████████████████████   ← 374 are exactly 0% (perfect)
  10- 20% |    8  █
  20- 30% |    7  █
  30- 40% |    4
  40- 50% |    4
  50- 60% |   20  ██
  60- 70% |   10  █
  70- 80% |   15  █
  80- 90% |   24  ██
  90-100% |  206  ██████████████████                   ← 131 are exactly 100% (never hit)
```

The distribution is **U-shaped**: **56%** of cases hit ≥90% of the time (374 hit *every* call),
**30%** miss ≥90% (131 *never* hit), only **~14%** in between. The worst 25% of cases account
for **94% of all misses**. The same GT shape can be always-hit for one case and always-miss for
another — the driver is the per-case MCTS trajectory, not the shape alone.

---

## 6. The always-miss cases — GT vs. the path the LLM takes

Script: `analyze_a4_alwaysmiss_paths.py`. CSV: `a4_alwaysmiss_paths.csv`.
131 cases where RAG **never** hit, categorized by dominant rollout path vs. GT:

| Category | Cases | What's happening |
|---|---:|---|
| **wrong_first_op** | **90 (69%)** | LLM's first operator ≠ GT's first operator |
| llm_no_op | 18 (14%) | LLM emits `NO_MORE_OPERATION` immediately (gives up) |
| no_structural_gt | 16 (12%) | GT is only `split`/`Date` — RAG can't help |
| fewer_ops_granularity | 4 (3%) | right first op, but collapses repeated ops |
| no_gt_entry | 2 | case absent from GT CSV → RAG disabled |
| other | 1 | LLM took the exact GT path but always included `terminal` (match needs strictly-longer) |

Wrong-first-op breakdown (GT first op → LLM first op):
`merge→groupby` 34, `union→merge` 24, `groupby→merge` 22, `union→groupby` 7.
**The LLM has a strong `groupby`/`merge` prior and systematically mishandles `union`/concat
pipelines** — 31/90 have a `union`-first GT but the LLM opens with `merge`/`groupby`.
10 of the 18 `llm_no_op` cases are long concat pipelines (the LLM won't chain many unions).

Example:
```
case 2_61   GT raw: ['concat','concat']     GT path: union>union>terminal
            LLM took: 39x groupby>terminal | 1x terminal
```

---

## 7. Accuracy by miss-rate bin (does low hit-rate cost correctness?)

Script: `analyze_a4_bin_accuracy.py`. CSV: `a4_bin_accuracy.csv`.
Correctness from `results_summary.csv` (`is_correct`).

| Miss-rate bin | Cases | Correct | % Correct |
|---|---:|---:|---:|
| 0–10%   | 379 | 356 | **93.9%** |
| 10–20%  | 8   | 0   | 0.0% |
| 20–30%  | 7   | 1   | 14.3% |
| 30–40%  | 4   | 2   | 50.0% |
| 40–50%  | 4   | 0   | 0.0% |
| 50–60%  | 20  | 20  | 100.0% |
| 60–70%  | 10  | 8   | 80.0% |
| 70–80%  | 15  | 11  | 73.3% |
| 80–90%  | 23  | 8   | 34.8% |
| 90–100% | 205 | 93  | **45.4%** |
| **All** | **675** | **499** | **73.9%** |

- **RAG hit-rate strongly predicts correctness:** 0–10% miss → **93.9%** correct vs.
  90–100% miss → **45.4%** correct (roughly halved).
- **But the always-miss bucket isn't hopeless** — ~45% are still correct (the LLM solves them
  without RAG, often because it's "close": reorderings/granularity differences).
- The cases where low RAG coverage **actually costs accuracy** are the ~112 always-miss cases
  that are also wrong (205 − 93) — the target for better rollout/RAG alignment.

### 7b. a4 (RAG) vs No-RAG accuracy, same bins

Script: `analyze_a4_bin_accuracy_vs_norag.py`. CSV: `a4_bin_accuracy_vs_norag.csv`.
No-RAG correctness from the `mcts_pipeline_sim_*` / `mcts_pipeline_len2356_*` result dirs
(same MCTS, no RAG). All 675 binned cases have a matching no-RAG result.

| Miss-rate bin | Cases | a4 correct | a4 % | no-RAG correct | no-RAG % | Δ pts |
|---|---:|---:|---:|---:|---:|---:|
| 0–10%   | 379 | 356 | 93.9% | 347 | 91.6% | +2.4 |
| 10–20%  | 8   | 0   | 0.0%  | 0   | 0.0%  | +0.0 |
| 20–30%  | 7   | 1   | 14.3% | 1   | 14.3% | +0.0 |
| 30–40%  | 4   | 2   | 50.0% | 1   | 25.0% | +25.0 |
| 40–50%  | 4   | 0   | 0.0%  | 0   | 0.0%  | +0.0 |
| 50–60%  | 20  | 20  | 100.0%| 14  | 70.0% | **+30.0** |
| 60–70%  | 10  | 8   | 80.0% | 6   | 60.0% | +20.0 |
| 70–80%  | 15  | 11  | 73.3% | 9   | 60.0% | +13.3 |
| 80–90%  | 23  | 8   | 34.8% | 4   | 17.4% | +17.4 |
| 90–100% | 205 | 93  | 45.4% | 87  | 42.4% | +2.9 |
| **All** | **675** | **499** | **73.9%** | **469** | **69.5%** | **+4.4** |

**RAG's value is concentrated in the middle band, not the extremes:**

- **Top bin (0–10% miss): +2.4 pts only** — RAG fires constantly but the cases are already
  solvable (91.6% without RAG); RAG is largely redundant where it works best.
- **Bottom bin (90–100% miss): +2.9 pts only** — RAG essentially never fired, so it can't help
  the cases that need it most.
- **Middle bins (50–90% miss): +13 to +30 pts** — where RAG actually earns its keep (but only
  10–23 cases each).

**Overall RAG lift is +4.4 pts (73.9% vs 69.5%).** The upper-bound RAG helps far less than its
"perfect" setup suggests: its hits land on cases the LLM would solve anyway, while the
always-miss cases get almost no help. Closing the gap means making RAG fire on the hard cases.

### 7c. a4 vs global: accuracy and simulate RAG hit-rate per bin

Script: `analyze_a4_bin_global.py`. CSV: `a4_bin_global_compare.csv`. Same a4-defined bins,
all 675 cases also have a global result. RAG hit% = (sum simulate RAG hits) / (sum simulate
calls) across the bin's cases.

| Bin | Cases | a4 acc % | global acc % | a4 RAG hit % | global RAG hit % |
|---|---:|---:|---:|---:|---:|
| 0–10%   | 379 | 93.9% | 92.6% | 99.0% | 54.6% |
| 10–20%  | 8   | 0.0%  | 12.5% | 86.6% | 73.1% |
| 20–30%  | 7   | 14.3% | 14.3% | 75.8% | 41.7% |
| 30–40%  | 4   | 50.0% | 50.0% | 69.0% | 13.6% |
| 40–50%  | 4   | 0.0%  | 0.0%  | 56.1% | 48.4% |
| 50–60%  | 20  | 100.0%| 75.0% | 48.3% | 17.8% |
| 60–70%  | 10  | 80.0% | 80.0% | 35.0% | 28.1% |
| 70–80%  | 15  | 73.3% | 66.7% | 25.6% | 13.5% |
| 80–90%  | 23  | 34.8% | 34.8% | 14.6% | 6.7% |
| 90–100% | 205 | 45.4% | 44.9% | 3.1% | 6.3% |
| **All** | **675** | **73.9%** | **72.3%** | **23.9%** | **19.3%** |

- a4's RAG hit% is near-tautological with the bin (it defines them); the informative column is
  **global hit% on the same cases**.
- **Global fires much less than a4 in the good bins** (top bin 54.6% vs 99.0%) yet reaches almost
  the same accuracy (92.6% vs 93.9%) — these cases are solvable regardless.
- **The 90–100% bin flips it:** on a4's always-miss cases **global fires *more* (6.3% vs 3.1%)** —
  its diverse pool catches rollouts the single GT pipeline can't — **yet global acc (44.9%) ≈ a4
  (45.4%).** More hit-rate on hard cases → no accuracy gain.
- Overall global runs at 19.3% hit-rate vs a4's 23.9% but lands 72.3% vs 73.9% accuracy: a ~5-pt
  hit-rate gap costs only ~1.6 pts of accuracy — **simulate RAG hit-rate is a weak lever on final
  correctness**; the bottleneck is the rollout policy / the LLM's operator choice.

---

## Takeaways

1. The low simulate hit-rate (a4 23.8%, global 19.3%) is driven by **MCTS rollouts wandering
   onto operator prefixes RAG can't support** — in a4 because they diverge from the one GT path
   (85% of misses), in global because the exact multi-step sequence isn't among schema-neighbors
   (86% of misses at depth≥2).
2. **Operator standardization at the bin level is not the problem; operator *granularity/order*
   is** — multi-`UNION` pipelines and `merge↔groupby` reorderings dominate the failures.
3. Hit-rate is **bimodal and case-specific**: half the cases are essentially solved, a third are
   essentially hopeless.
4. **Levers that would help most:** (a) order-/granularity-tolerant prefix matching (multiset or
   first-op matching), (b) diversity-aware global→local retrieval, and (c) a rollout policy that
   commits to the right first operator (especially `union` for concat pipelines).

## Scripts & outputs

| Script | Produces |
|---|---|
| `analyze_a4_sim_misses.py` | a4 miss decomposition (console) |
| `analyze_global_sim_misses.py` | global @50/@100 replay + pool diversity; `global_pool_diversity_by_len.csv`, `global_pool_shape_frequency.csv`, `global_missing_sequence_patterns.csv` |
| `analyze_divergence_patterns.py` | `a4_divergence_patterns.csv`, `a4_divergence_by_gt_shape.csv`, `a4_divergence_by_rollout.csv` |
| `analyze_a4_per_case_missrate.py` | per-case histogram; `a4_per_case_miss_rate.csv` |
| `analyze_a4_alwaysmiss_paths.py` | always-miss deep dive; `a4_alwaysmiss_paths.csv` |
| `analyze_a4_bin_accuracy.py` | accuracy by bin; `a4_bin_accuracy.csv` |
| `analyze_a4_bin_accuracy_vs_norag.py` | a4 vs no-RAG accuracy by bin; `a4_bin_accuracy_vs_norag.csv` |
| `analyze_a4_bin_global.py` | a4/no-RAG/global accuracy + avg RAG hits by bin; `a4_bin_global_compare.csv` |

> Note: the global scripts require the `env/` virtualenv (`env/bin/python`) for
> `torch`/`transformers`/`sentence-transformers`; the a4-only scripts run under plain `python3`.
