# mcts_search.py — MCTS Schema Transformation Search

Monte Carlo Tree Search over the operator space for schema transformation.
Each MCTS iteration selects a node, expands it (proposes candidate next operators),
simulates the result (generates and executes Python code), scores the output,
and backpropagates the reward.

**Run from the project root (`~/transchema/`):**
```bash
python3 Langraph/mcts_search.py [args]
```

---

## Arguments

### Case selection

| Argument | Type | Default | Description |
|---|---|---|---|
| `--length` | int | `2` | Length bucket to run (e.g. 1, 4, 9) |
| `--id_start` | int | `0` | First case ID to run (inclusive) |
| `--id_end` | int | `0` | Last case ID to run (inclusive) |
| `--cases` | str+ | `None` | Explicit list of case IDs (e.g. `1_41 4_18 9_70`). **Overrides** `--length` / `--id_start` / `--id_end` |

### Model & token budget

| Argument | Type | Default | Description |
|---|---|---|---|
| `--model` | str | `gpt-4.1-mini` | LLM model identifier |
| `--token_limit` | int | `128000` | Maximum tokens per prompt |

### Data sampling

| Argument | Type | Default | Description |
|---|---|---|---|
| `--target_per` | float | `10.0` | Target table sample percentage |
| `--is_perc` | bool | `False` | Use percentage-based sampling instead of row count |
| `--target_length` | int | `3` | Number of target table sample rows shown in the prompt |
| `--source_length` | int | `3` | Number of source table sample rows shown in the prompt |

### MCTS search control

| Argument | Type | Default | Description |
|---|---|---|---|
| `--mcts_iterations` | int | `5` | Total MCTS budget (number of iterations) |
| `--early_stopping` | int | `5` | Stop if best score does not improve for this many consecutive iterations |

### Simulation strategy

| Argument | Type | Default | Choices | Description |
|---|---|---|---|---|
| `--simulation` | str | `pipeline` | `pipeline`, `operator` | **pipeline** — one LLM call generates the complete Python script from the partial operator plan. **operator** — mirrors the multi-step process: iterates `get_next_operator` + configure prompts one step at a time, then generates Python code. |

### Reward signal

| Argument | Type | Default | Choices | Description |
|---|---|---|---|---|
| `--reward` | str | `score` | `score`, `validation`, `partial` | **score** — continuous `relative_csv_score` (FD + column map + distribution). **validation** — binary 1.0 if hard-match validation passes else 0.0. **partial** — fuzzy column-match ratio (matched target cols / total target cols). |

### Validation

| Argument | Type | Default | Choices | Description |
|---|---|---|---|---|
| `--validation` | str | `hard_match` | `hard_match`, `autopipeline` | **hard_match** — `compare_lists_matching`, gives partial credit. **autopipeline** — `compare_tables_matching`, binary match. |

### Critique

| Argument | Type | Default | Choices | Description |
|---|---|---|---|---|
| `--mcts_critique_mode` | str | `none` | `none`, `simulate`, `best` | **none** — critique disabled. **simulate** — critique runs after each iteration when score < 1.0. **best** — critique runs once on the final best script. |
| `--no_static_hints` | flag | off | — | Suppress static hint injection (`CRITIQUE_HINT_IDS`) from the critique prompt. Static hints are on by default. |

### Hints

| Argument | Type | Default | Description |
|---|---|---|---|
| `--hint_source` | str | `none` | Dynamic data-specific hint source. `none` = no dynamic hints. `v1_text` = human-readable text hints derived from the actual CSV data (join candidates, group-by candidates, table matching). Injected into `mcts_expand` (operator selection) and `mcts_simulate` / operator-level simulation prompts. |
| `--fd_flag` | int | `0` | Include functional dependency hints in prompts (`1` = on) |
| `--join_flag` | int | `0` | Join hint generation flag (passed to dynamic hint engine) |
| `--aggregate_flag` | int | `0` | Aggregate hint generation flag (passed to dynamic hint engine) |

### Few-shot & anonymisation

| Argument | Type | Default | Description |
|---|---|---|---|
| `--few_shot` | int | `0` | Few-shot examples flag |
| `--anon_flag` | bool | `False` | Anonymise schema/table names in prompts |

### Benchmark & output

| Argument | Type | Default | Choices | Description |
|---|---|---|---|---|
| `--benchmark` | str | `github` | `github`, `monteprep` | Dataset benchmark to run on |
| `--experiment_name` | str | `mcts_run` | — | Label for the run; logs go to `logs_langraph/<experiment_name>/`, results to `results_langraph/<experiment_name>_<timestamp>/` |
| `--result_dir` | str | `results_langraph` | — | Base directory for result CSVs |

---

## Output

Each run produces:
- **Logs**: `logs_langraph/<experiment_name>/<case_id>.log`
- **Results CSV**: `results_langraph/<experiment_name>_<timestamp>/results_summary.csv`

CSV fields: `case_id`, `is_correct`, `cost`, `latency_seconds`, `best_score`, `operation_history`, `timestamp`, `status`, `error`.

---

## Example Commands

### Pipeline simulation (baseline)

Single run, L1 cases 0–100, partial reward:
```bash
python3 Langraph/mcts_search.py \
    --length 1 --id_start 0 --id_end 100 \
    --validation autopipeline \
    --benchmark github \
    --model gpt-4.1-mini \
    --token_limit 12000 \
    --source_length 3 --target_length 3 \
    --reward partial \
    --experiment_name mcts_github_partial_l1 \
    --mcts_critique_mode simulate
```

Pipeline simulation, 30 iterations with early stopping, L1/L4/L9:
```bash
python3 Langraph/mcts_search.py \
    --length 1 --id_start 0 --id_end 100 \
    --validation autopipeline --benchmark github \
    --model gpt-4.1-mini --token_limit 12000 \
    --source_length 3 --target_length 3 \
    --reward partial \
    --mcts_iterations 30 --early_stopping 15 \
    --experiment_name mcts_github_partial_l1_iter30_es15 \
    --mcts_critique_mode simulate
```

Pipeline simulation with critique, L4 split across two parallel processes:
```bash
python3 Langraph/mcts_search.py \
    --length 4 --id_start 15 --id_end 57 \
    --mcts_iterations 10 --mcts_critique_mode simulate \
    --validation autopipeline \
    --experiment_name overnight_mcts_l4_15_57 \
    &> logs_langraph/mcts_l4_15_57.log &

python3 Langraph/mcts_search.py \
    --length 4 --id_start 58 --id_end 100 \
    --mcts_iterations 10 --mcts_critique_mode simulate \
    --validation autopipeline \
    --experiment_name overnight_mcts_l4_58_100 \
    &> logs_langraph/mcts_l4_58_100.log &
```

### Operator-driven simulation (opsim)

Operator-level simulation on specific cases, 10 iterations:
```bash
python3 Langraph/mcts_search.py \
    --cases 4_30 4_31 4_34 4_40 4_41 4_82 4_36 4_72 4_85 4_88 \
    --model gpt-4.1-mini \
    --token_limit 12000 \
    --source_length 3 --target_length 3 \
    --mcts_iterations 10 \
    --mcts_critique_mode simulate \
    --validation autopipeline \
    --simulation operator \
    --reward partial \
    --experiment_name mcts_opsim_batch1
```

### With v1-text dynamic hints

Pipeline simulation + v1-text hints on L1, first 10 cases:
```bash
python3 Langraph/mcts_search.py \
    --length 1 --id_start 0 --id_end 9 \
    --validation autopipeline \
    --model gpt-4.1-mini --token_limit 12000 \
    --source_length 3 --target_length 3 \
    --reward partial \
    --hint_source v1_text \
    --experiment_name mcts_v1text_l1_0_9 \
    --mcts_critique_mode simulate
```

Operator simulation + v1-text hints:
```bash
python3 Langraph/mcts_search.py \
    --length 1 --id_start 0 --id_end 9 \
    --validation autopipeline \
    --model gpt-4.1-mini --token_limit 12000 \
    --source_length 3 --target_length 3 \
    --reward partial \
    --simulation operator \
    --hint_source v1_text \
    --experiment_name mcts_opsim_v1text_l1_0_9 \
    --mcts_critique_mode simulate
```
