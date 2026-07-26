# Running MMTU's Transform-by-output-target-schema task against local github-pipelines data

This documents the workflow for running MMTU's `Transform-by-output-target-schema` task
(the "target-schema" prompt) against the `github-pipelines` benchmark using data that's
already available locally at `autopipeline-benchmarks/github-pipelines`, scoring with the
same "autopipeline" validation `Langraph/mcts_search.py` uses (`--validation autopipeline`),
instead of downloading MMTU's OneDrive raw-data release.

Two scripts, both in `MMTU/`:
- `run_openai_task.py` — inference (queries an OpenAI model for each prompt)
- `evaluate_autopipeline.py` — scoring (executes the generated code, compares to `target.csv`)

## 1. One-time data setup

### 1a. Download the MMTU prompt dataset (if `MMTU/mmtu.jsonl` doesn't already exist)
```bash
cd MMTU
source ../env/bin/activate
python3 -c "
from datasets import load_dataset
ds = load_dataset('MMTU-benchmark/MMTU', split='train')
ds.to_json('mmtu.jsonl', lines=True)
"
```
This is the full ~28K-row benchmark (25 tasks). Not gated — no HF token needed. It contains
prompts + metadata only; it does **not** contain the raw source/target CSVs needed to execute
and score generated code.

### 1b. Bridge `MMTU_HOME` to the local benchmark data
The official metadata's `case_path` field points at
`$MMTU_HOME/data/Transform-by-output-target-schema/sample1000-3shots/github-pipelines/<case>`.
Rather than downloading MMTU's separate OneDrive raw-data release, symlink that path straight
at the local `autopipeline-benchmarks/github-pipelines` clone (read-only reference — nothing
in that repo gets touched):
```bash
export MMTU_HOME=/home/asurite.ad.asu.edu/jrtandel/transchema/MMTU
mkdir -p "$MMTU_HOME/data/Transform-by-output-target-schema/sample1000-3shots"
ln -s /home/asurite.ad.asu.edu/jrtandel/transchema/autopipeline-benchmarks/github-pipelines \
      "$MMTU_HOME/data/Transform-by-output-target-schema/sample1000-3shots/github-pipelines"
```
`export MMTU_HOME=...` needs to be set in every shell session before running either script below.

Sanity check:
```bash
ls "$MMTU_HOME/data/Transform-by-output-target-schema/sample1000-3shots/github-pipelines/length1_11"
# should list test_0.csv, target.csv, training_0.csv, ...
```

Note: 2 of the 672 official cases (`length3_30`, `length6_59`) have had their files deleted
locally in `autopipeline-benchmarks` (uncommitted `git status` deletion, not something these
scripts do) — they fail gracefully during evaluation (`reason: sandbox_error`) rather than
blocking the run. Restore them with `git checkout -- <path>` in that repo if you want full
672/672 coverage.

## 2. Run inference across all cases, with multiple workers

`run_openai_task.py` reads `mmtu.jsonl`, filters to the task/dataset/length you want, and
queries the model with `--n_parallel` concurrent worker threads (all writing to one output
file, safely serialized with a lock — one process, one file, no corruption risk).

Run everything in a single call:
```bash
export MMTU_HOME=/home/asurite.ad.asu.edu/jrtandel/transchema/MMTU
cd MMTU
python3 run_openai_task.py \
    --task Transform-by-output-target-schema \
    --dataset github-pipelines \
    --model gpt-4.1-mini \
    --n_parallel 10
```
Writes to `mmtu.<model_tag>.result.jsonl` (dots in the model name get sanitized to dashes for
the filename, e.g. `gpt-4.1-mini` → `mmtu.gpt-4-1-mini.result.jsonl`).

Useful flags:
- `--length N` — scope to one pipeline-length bucket (parsed from `test_case`, e.g. `length3_*`)
- `--limit N` — smoke-test on just the first N rows before committing to a full run
- `--mmtu_jsonl path.jsonl` — point at any correctly-shaped jsonl instead of the default
  `mmtu.jsonl` (see §4 for re-running just the failed cases against a different model)
- `--output_dir DIR` — write results somewhere other than the current directory (created
  automatically if missing)
- Reruns **resume** automatically — already-completed rows (matched by `metadata`) are
  skipped, so it's safe to re-invoke the same command after an interruption

`o4-mini` and other OpenAI reasoning models work with this script as-is (it already defaults
to `temperature=1.0`, the only value those models accept — anything else 400s).

### Local/Ollama models (e.g. Qwen3:32B on Sol)

Any `--model` containing "qwen" (case-insensitive, e.g. `qwen3:32b`, `qwen2.5:32b`) routes to
a local Ollama server instead of OpenAI's cloud API — no `--api_key` needed. This reuses the
same base-URL resolution `llm/llm_models.py`'s `LLMClient` uses (honors `$OLLAMA_HOST`, same
convention as `Langraph/mcts_search.py`), so it works out of the box on Sol without further
setup. Qwen3 is a "thinking" model — the script automatically sends `extra_body={"think":
False}` so the response budget goes to the actual code instead of hidden reasoning tokens
(matches `LLMClient`'s behavior; Qwen2.5 doesn't need this and doesn't get it).

Local models default to a much longer per-request timeout (`$TRANSCHEMA_OLLAMA_HTTP_TIMEOUT`,
3600s) than the cloud default (90s), since a 32B model running locally is far slower than a
hosted API call. Override either with `--timeout <seconds>`.
```bash
python3 run_openai_task.py \
    --task Transform-by-output-target-schema \
    --dataset github-pipelines \
    --model qwen3:32b \
    --n_parallel 4
```

## 3. Score with autopipeline validation

`evaluate_autopipeline.py` extracts each row's generated code, executes it in a sandboxed
per-case directory against the real `test_N.csv`→`source_N.csv` files, and compares the
resulting `output.csv` to `target.csv` using `validation.hard_match.compare_tables_matching`
— the same semantic, column-order/name-independent matcher `mcts_search.py` uses under
`--validation autopipeline`. This is separate from and more forgiving than MMTU's own
`evaluate.py`/`TransformByTargetSchemaEvaluator` (which requires exact `columns == columns`
equality) — both are available side by side.

```bash
cd MMTU
python3 evaluate_autopipeline.py mmtu.gpt-4-1-mini.result.jsonl --workers 10
```
Prints and saves a per-length breakdown (`n`, `n_correct`, `acc`) plus an overall row, and a
`reason` breakdown (`scored` / `exec_error` / `exec_timeout` / `sandbox_error` / `no_code_block`).

Useful flags:
- `--length N` — evaluate just one length bucket
- `--workers N` — parallel worker processes (each case runs in its own sandbox dir, safe to
  parallelize; default is 1, which is slow for large result sets)
- `--timeout N` — per-case execution timeout in seconds (default 10)

Output:
- `autopipeline_eval_results/<model_tag>_details.csv` — one row per case (`test_case`,
  `length`, `is_correct`, `reason`, `error_detail`)
- `autopipeline_eval_results/<model_tag>_summary.csv` — the per-length + overall table

## 4. Example: re-running only the failed cases against a different model

Filter the previous model's failures out of `mmtu.jsonl` into their own file, then point
`run_openai_task.py` at it directly — no code changes needed, since it accepts any
correctly-shaped `--mmtu_jsonl`:
```bash
cd MMTU
source ../env/bin/activate
python3 -c "
import json
import pandas as pd

details = pd.read_csv('autopipeline_eval_results/gpt-4-1-mini_details.csv')
failed_cases = set(details[details['is_correct'] == False]['test_case'])

with open('mmtu.jsonl') as f_in, open('mmtu_failed_cases.jsonl', 'w') as f_out:
    for line in f_in:
        row = json.loads(line)
        if row['task'] != 'Transform-by-output-target-schema':
            continue
        m = json.loads(row['metadata'])
        if m['test_case'] in failed_cases:
            f_out.write(line)
"

export MMTU_HOME=/home/asurite.ad.asu.edu/jrtandel/transchema/MMTU
python3 run_openai_task.py \
    --task Transform-by-output-target-schema \
    --model o4-mini \
    --mmtu_jsonl mmtu_failed_cases.jsonl \
    --output_dir results_o4mini_failed \
    --n_parallel 10

python3 evaluate_autopipeline.py results_o4mini_failed/mmtu.o4-mini.result.jsonl --workers 10
```

## Known findings worth knowing before digging into results

- Accuracy drops sharply as pipeline length increases — "length" in this benchmark mostly
  means *number of source tables to join/merge* (avg 1.4 at length1 vs. ~20 at length9, one
  case has 222), not just number of transform steps.
- A recurring `MergeError: ... duplicate columns {'Unnamed: 0_x'}` execution failure comes
  from a stray index column present in the raw CSVs but hidden from the LLM's prompt (the
  prompt-builder uses `index_col=0` when rendering samples) — `evaluate_autopipeline.py`
  already strips this column when materializing the sandbox, so this is handled, but it's
  worth knowing about if you see it in older result sets evaluated before that fix.
- At high lengths, the "Target Schema" preview (`FirstNRowsProcessor(n=10)` truncation, same
  as the source tables) often coincidentally looks identical to a 10-row source sample,
  leading models to wrongly `.head(10)` or `.drop_duplicates()` a correct full concatenation
  down to a tiny table. This is a genuine prompt-design ambiguity, not fixable at evaluation
  time — it needs a different prompt to test.
