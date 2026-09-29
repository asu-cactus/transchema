# data_transformation_start.py

This script runs selected data-transformation benchmark cases through AgentFlow, logs each run, and writes per-case result artifacts plus a final summary.

## What it does

- Selects cases by `len_id` + `target_id` (explicit list or range mode).
- Builds case-specific prompts with `get_prompt(prompt_type="get_case_info")`.
- Runs the AgentFlow solver for each case.
- Saves:
  - text result summary
  - full JSON output
  - detailed logs
  - error report (if a case fails)

## Prerequisites

- Project environment set up (see `AgentFlow/README.md`).
- API keys configured in `AgentFlow/agentflow/.env` (especially `OPENAI_API_KEY` for OpenAI models).
- Benchmarks and JSON metadata present at:
  - `autopipeline-benchmarks/github-pipelines`
  - `data/chatgpt_github_ms.json`
  - `data/chatgpt_github_ss.json`

## Configure cases

Edit constants near the top of `AgentFlow/data_transformation_start.py`.

### Option A: explicit case list (default)

```python
LEN_ID = 4
TARGET_IDS = [31, 35, 74, 79, 97]
```

This runs: `4_31`, `4_35`, `4_74`, `4_79`, `4_97`.

### Option B: range mode

Set:

```python
TARGET_IDS = None
MAX_LEN_ID = 4
TARGET_ID_START = 1
TARGET_ID_END = 60
```

Then cases are derived by `get_test_cases_ids(...)`.

## Runtime knobs

Also configurable in `AgentFlow/data_transformation_start.py`:

- `LLM_ENGINE_NAME` (default: `gpt-4.1-mini`)
- `PLANNER_GRANULARITY`:
  - `"pipeline"` uses pipeline-level tools
  - `"operator"` uses operator-level tools
- `EXECUTE_PIPELINE` (default: `False`)
- `START_AGAIN_CLEAR_HISTORY` (default: `False`)
- `RESULTS_DIR` (default output root)

## Run

From repository root:

```bash
cd /home/local/ASUAD/jrtandel/transchema
python AgentFlow/data_transformation_start.py
```

You can also run from `AgentFlow/`:

```bash
cd /home/local/ASUAD/jrtandel/transchema/AgentFlow
python data_transformation_start.py
```

## Output layout

By default, outputs are under:

`AgentFlow/results_pipeline_execution_experiments_len_4_failed_cases/`

Per case:

- `case_<lenid_targetid>/<lenid_targetid>_result.txt`
- `case_<lenid_targetid>/<lenid_targetid>_full_output.json`
- `case_<lenid_targetid>/logs/`
- `case_<lenid_targetid>/<lenid_targetid>_error.txt` (only on failure)

At the end, the script prints a console summary with counts for:

- `Correct`
- `Incorrect`
- `Errors`

## Notes

- Ground-truth verification reads `target.csv` in each benchmark case folder. If missing, a warning is printed and verification may be limited.
- If you change `PLANNER_GRANULARITY`, make sure tool behavior and expected outputs match your experiment goals.
