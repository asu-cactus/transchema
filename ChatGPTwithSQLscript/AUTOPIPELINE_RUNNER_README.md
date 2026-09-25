# Auto-Pipeline SQL Baseline Runner

Runs `auto_pipeline_join.py` — the ChatGPT+SQL baseline (LLM writes Postgres SQL,
including `COPY` of the full source CSVs, then the result is validated against the
full `target.csv`) — over the `autopipeline-benchmarks/github-pipelines` benchmark
(700 real-world pipeline cases, grouped as `length1`..`length9`, ~100 cases each).

This is the SQL-generation baseline; the MCTS/pandas pipeline lives in `Langraph/`
and `BAT/` and has its own runner (`BAT/ITERATIVE_RUNNER_README.md`).

## Prerequisites

```bash
source /home/asurite.ad.asu.edu/jrtandel/transchema/env/bin/activate
export OPENAI_API_KEY=...          # if not already set
```

Postgres connection defaults to TCP with hardcoded dev credentials (`util.py`), which
don't authenticate in every environment. If you get a GSSAPI/password error, connect
over the local Unix socket instead by setting `PGHOST` to empty and `PGUSER` to your
OS user:
```bash
export PGHOST=""
export PGUSER="$USER"
```

## Quick Start — run one whole length

```bash
cd /home/asurite.ad.asu.edu/jrtandel/transchema/ChatGPTwithSQLscript
python3 auto_pipeline_join.py \
    --len 1 \
    --start_target_id 0 \
    --end_target_id 99 \
    --validation autopipeline \
    --experiment_name length1_full \
    --model gpt-4.1-mini
```

This runs every `Target1_0`..`Target1_99` case, scores each with `compare_tables_matching`
(the same function `Langraph/mcts_search.py` and `BAT/run_cases_iteratively.py` use for
their own `--validation autopipeline`), and writes everything under
`logs/length1_full_{TIMESTAMP}/`.

### Index ranges per length

Case indices aren't perfectly uniform across lengths — some have gaps. It's safe to
always pass `0` and the max below as `--start_target_id`/`--end_target_id`; any missing
index is skipped with a logged warning rather than failing the run.

| `--len` | cases | `--end_target_id` |
|---|---|---|
| 1 | 100 | 99 |
| 2 | 100 | 99 |
| 3 | 100 | 100 (one gap) |
| 4 | 100 | 99 |
| 5 | 98  | 97 |
| 6 | 99  | 99 (one gap) |
| 9 | 101 | 100 |

To run a different length, just swap `--len` and `--end_target_id`, e.g. length 9:
```bash
python3 auto_pipeline_join.py \
    --len 9 --start_target_id 0 --end_target_id 100 \
    --validation autopipeline --experiment_name length9_full --model gpt-4.1-mini
```

### Run a subset instead

```bash
python3 auto_pipeline_join.py \
    --len 1 --start_target_id 10 --end_target_id 20 \
    --validation autopipeline --experiment_name length1_debug --model gpt-4.1-mini
```

## Output

Everything for a run goes to `logs/{experiment_name}_{TIMESTAMP}/`:

- **`results.csv`** — one row per case, written and fsynced immediately after each
  case finishes (not buffered to the end), so an interrupted run keeps everything
  completed so far. Columns: `target`, `case`, `n_sources`, `model`,
  `validation_method`, `accuracy`, `correct`, `detail`, `error`, `prompt_tokens`,
  `completion_tokens`, `cost_usd`, `llm_latency_seconds`, `total_latency_seconds`.
- **`prompts_responses.jsonl`** — one JSON object per case with the full prompt text,
  full LLM response (the generated SQL), token usage, and LLM call latency. Use this
  to recompute cost under different pricing, or to inspect exactly what was sent/received.
- **`run.log`** — detailed trace: prompt sizes, the generated SQL for every case,
  validation diagnostics, and any exceptions.

## Validation Strategies

Pass via `--validation`:

| Value | What it does |
|---|---|
| `inbuilt` (default) | `join.py`'s `validation()` — positional column comparison (not by name), rows sorted first. The original method used throughout this file's development. |
| `hard_match` | `compare_lists_matching` from the repo-root `validation/hard_match.py` — per-column partial credit, columns matched by **name** (case-normalized against Postgres's lowercasing of unquoted identifiers). Same default `Langraph/mcts_search.py` and `BAT/run_cases_iteratively.py` use. |
| `autopipeline` | `compare_tables_matching` (same module) — matches columns by **data content**, not name; all-or-nothing per case (no partial credit). Use this one for numbers directly comparable to the MCTS pipeline's own `--validation autopipeline` runs. |

`hard_match`/`autopipeline` need `python-Levenshtein`, which is in the repo-root venv
(`env/`) but may not be in other environments — use `source env/bin/activate` as above.

## Cost & Time Estimate

From an actual `gpt-4.1-mini` run of length 1 (90 of the 100 cases, `hard_match`):
**$0.00136/case, 8.6s/case average.** A full 100-case length should cost roughly
**$0.10–0.15** and take **~15–20 minutes**, single-threaded. Larger/more complex
cases (bigger CSVs, more source tables — `length9` in particular) will run slower and
cost somewhat more per case; check `results.csv`'s `cost_usd`/`total_latency_seconds`
columns as a run progresses rather than assuming this estimate holds exactly.

## Monitoring Progress

```bash
# Watch the live log
tail -f logs/length1_full_*/run.log

# Count completed cases so far (results.csv grows incrementally)
wc -l logs/length1_full_*/results.csv

# Running accuracy so far
python3 -c "
import glob, pandas as pd
path = sorted(glob.glob('logs/length1_full_*/results.csv'))[-1]
df = pd.read_csv(path)
print(f\"{df['correct'].sum()}/{len(df)} correct so far ({path})\")
"
```

## Notes

- **`--model`** defaults to `gpt-4-1106-preview` (`gpt.py`'s `DEFAULT_MODEL`), which
  404s on at least some API keys — pass `--model gpt-4.1-mini` or `--model o4-mini`
  explicitly unless you know your key has access to it.
- **Case folders can contain leftover artifacts from other methods' prior runs**
  (`target_multisource*.csv`, `python_recovered*.py`, etc.) — this runner only ever
  reads `test_*.csv`/`training_*.csv`/`target.csv` from the benchmark JSON
  (`data/chatgpt_github_ss.json`/`chatgpt_github_ms.json`) and the case folder's
  `test_*.csv` files for the full data load; it never touches those other files.
- Full source/target CSVs are loaded into Postgres via server-side `COPY`, which
  requires the Postgres process to have OS-level read access to the CSV paths — true
  by default here since everything runs on one machine, but worth knowing if Postgres
  ever moves to a separate host/container.
