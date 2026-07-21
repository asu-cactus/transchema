# Iterative MCTS Experiment Runner

Scripts for running MCTS experiments case-by-case with automatic result archival.

## Quick Start

### Run GitHub-Pipelines (recommended)
```bash
bash run_github_pipelines.sh
```

This will:
- Run cases for length 1 (0-99), 4 (0-99), and 9 (0-100)
- Save results after each length completes
- Archive to `results_archive/` with timestamped filenames
- Continue even if individual cases fail

### Run a Single Length
To run just one length (e.g. all of length 1, cases 0-99) on github-pipelines with autopipeline
validation, without editing the script's defaults:
```bash
source /home/asurite.ad.asu.edu/jrtandel/transchema/env/bin/activate
python3 run_cases_iteratively.py \
    --length_type 1 \
    --start_num 0 \
    --end_num 100 \
    --base_path /home/asurite.ad.asu.edu/jrtandel/transchema/autopipeline-benchmarks/github-pipelines \
    --result_dir result/github-pipelines/gpt-4.1-mini/execution \
    --predict_dir predict/github-pipelines/gpt-4.1-mini/execution \
    --validation autopipeline
```
Swap `--length_type` to `4` or `9` for the other lengths, and `--base_path`/`--result_dir`/`--predict_dir`
to the `monteprep-pipelines` paths (see below) to run that benchmark instead.

### Run Custom Configuration
```bash
python3 run_cases_iteratively.py \
    --length_type 4 \
    --start_num 0 \
    --end_num 100 \
    --base_path /path/to/benchmark \
    --result_dir result/dir/path \
    --predict_dir predict/dir/path \
    --validation autopipeline
```

## Output

### Master CSV Files
After each length completes, you'll find:
- **Timestamped**: `results_archive/master_results_github-pipelines_length{N}_{TIMESTAMP}.csv`
- **Latest**: `results_archive/master_results_github-pipelines_length{N}_latest.csv`

Columns in CSV:
- `case_id`: Identifier (e.g., length1_42)
- `length_type`: Length type (1, 4, or 9)
- `num`: Case number
- `accuracy`: 1.0 if perfect match, 0.0 otherwise
- `column_similarity`: Similarity score (0.0-1.0). Under `--validation autopipeline` this is
  always equal to `accuracy` (1.0 or 0.0) — see [Validation Strategies](#validation-strategies).
- `prompt_tokens`: Tokens used in prompt
- `completion_tokens`: Tokens in completion
- `total_tokens`: Total tokens used
- `latency_seconds`: Execution time
- `estimated_cost`: Estimated API cost

### Logs
- `logs/iterate_cases_{TIMESTAMP}.log` — main progress log
- `logs/mcts_length{N}_{M}.txt` — individual case MCTS output
- `logs/llm_queries_{MODEL}.jsonl` — LLM query trace (if saved)

## Validation Strategies

Pass `--validation` to control how each case's generated table is scored against `target.csv`:

| Value | What it does |
|---|---|
| `hard_match` (default) | Evaluator's own scoring (`calculate_similarity` / `calculate_column_similarity` in `src/utils/evaluator.py`) — per-cell numeric/string closeness with partial credit, matched by column **name**. |
| `autopipeline` | `compare_tables_matching` from the shared `validation/hard_match.py` at the repo root — the same function `Langraph/mcts_search.py` uses for `--validation autopipeline`. Matches columns by **content** (via `compare_series`), not by name, and is all-or-nothing: `accuracy` and `column_similarity` come out identical (both `1.0` or both `0.0`). Use this when you want BAT's scoring to be directly comparable to the Langraph MCTS pipeline's numbers.

`--validation autopipeline` pulls in `validation/autopipeline_match.py`, which needs `Levenshtein` — not
in BAT's own `requirements.txt`. Activate the repo-root virtualenv first:
```bash
source /home/asurite.ad.asu.edu/jrtandel/transchema/env/bin/activate
python3 run_cases_iteratively.py \
    --length_type 1 \
    --start_num 0 \
    --end_num 10 \
    --validation autopipeline
```

`compare_tables_matching` prints its own diagnostics (`THEY ARE OF SAME LENGTH: X Y`, `map_num = N MATCHED`, `didn't find corresponding columns for <col>`) while it runs — these only show up if you run `python3 src/utils/evaluator.py ...` directly. `run_cases_iteratively.py` calls the evaluator as a subprocess with `capture_output=True` and discards stdout on success, so you won't see them through the iterative runner even though the validation is running correctly.

### A note on this benchmark's data folders

Each case folder (e.g. `length1_0/`) can contain leftover output artifacts from *other* methods' prior runs on the same case — `target_multisource.csv`, `target_multisource_mcts.csv`, `target_multisource_cot.csv`, etc. These are near-answer files and are **excluded** from both the LLM's prompt (`src/mcts/data.py`), the MCTS search's own reward loop (`src/mcts/reward.py`), and the evaluator's exec environment (`src/utils/evaluator.py`) — only `test_*`/`training_*` source files and a schema-only 5-row preview of the real `target.csv` are ever exposed. If you add new source/target files to a benchmark folder, keep this naming convention (`target*` reserved for ground truth) so the exclusion keeps working.

## Features

✅ **Resilient**: Continues processing even if individual cases fail or timeout  
✅ **Safe**: Results automatically archived after each length  
✅ **Traceable**: Timestamped archives prevent overwrites  
✅ **Flexible**: Configurable paths, ranges, and models  
✅ **Efficient**: Cleans up intermediate JSON results to save disk space  

## Configuration

Edit `run_cases_iteratively.py` to change defaults:
```python
BASE_PATH = "..."              # Benchmark data location
RESULT_DIR = "..."             # Where MCTS outputs JSON results
PREDICT_DIR = "..."            # Where evaluation outputs go
LENGTH_TYPE = 1                # Default length type
START_NUM = 0                  # Default start case
END_NUM = 100                  # Default end case
CLEANUP_RESULTS = True         # Delete intermediate JSONs after eval (override per-run with --no_cleanup)
VALIDATION = "hard_match"      # "hard_match" or "autopipeline" (override per-run with --validation)
```

Both `CLEANUP_RESULTS` and `VALIDATION` can also be set per-invocation via `--no_cleanup` and `--validation`
without editing the file — see [Validation Strategies](#validation-strategies) and the debugging example below.

## Troubleshooting

**Master CSV not created?**
- Check `logs/iterate_cases_*.log` for errors
- Verify benchmark data exists at base_path
- Ensure evaluator has access to target.csv files

**Cases timing out?**
- Check `logs/mcts_lengthX_Y.txt` for LLM errors
- May need to increase timeout in `run_command()` (currently 1 hour)
- Check memory usage if processes are killed

**Duplicate results?**
- Old CSVs in `predict_dir/` get overwritten by evaluator
- Use `results_archive/` to keep timestamped copies
- Latest links always point to most recent run

## Advanced Usage

### Run subset of cases:
```bash
python3 run_cases_iteratively.py \
    --length_type 1 \
    --start_num 10 \
    --end_num 20
```

### Run monteprep-pipelines:
```bash
python3 run_cases_iteratively.py \
    --length_type 1 \
    --base_path /path/to/monteprep-pipelines \
    --result_dir result/monteprep-pipelines/gpt-4.1-mini/execution \
    --predict_dir predict/monteprep-pipelines/gpt-4.1-mini/execution
```

### Debug a specific case (keep the intermediate JSON, use autopipeline validation):
```bash
python3 run_cases_iteratively.py \
    --length_type 1 \
    --start_num 2 \
    --end_num 3 \
    --result_dir result/.../debug \
    --predict_dir predict/.../debug \
    --validation autopipeline \
    --no_cleanup
```
`--no_cleanup` keeps `result/.../length{N}/length{N}_{M}.json` around after evaluation instead of deleting
it, so you can re-run the exact generated script against `read_csv_files`/`compare_tables_matching`
yourself without paying for another MCTS/LLM run.

## Monitoring Progress

```bash
# Watch latest log in real-time
tail -f logs/iterate_cases_*.log

# See failed cases
grep "Failed:" logs/iterate_cases_*.log

# Count completed cases
wc -l results_archive/master_results_github-pipelines_length1_latest.csv
```
