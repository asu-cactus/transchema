# BAT with target example rows: running on another machine

One model per machine, all with `--target_examples 3`, on both benchmarks, run one after the other:
GitHub-pipelines (698 cases, L1 to L9), then smart-building v2 (105 cases, groups 1 to 15). 20 workers share
one queue per benchmark (a freed worker takes the next case).

| Machine | Command | Model |
|---|---|---|
| this one | `bash run_bat_target_examples.sh oss120b` | `dmx-gpt-oss-120b` |
| second | `bash run_bat_target_examples.sh flash` | `dmx-deepseek-v4-flash` |
| third | `bash run_bat_target_examples.sh pro` | `dmx-deepseek-v4-pro` |

A second argument picks the benchmark: `bash run_bat_target_examples.sh flash smartbuilding` (or `github`; default `both`).

## One-time setup on each new machine

1. **Code.** Clone the repo and check out `ablation_studies`. The changes this needs (`--target_examples`,
   the `dmx-*` entries in `BAT/src/llm/config.py`, the shared-queue launcher) must be committed and pushed
   first; at the time of writing they are uncommitted on the main machine.
2. **Python env.** `python3 -m venv ~/bat_env && source ~/bat_env/bin/activate`, then
   `pip install -r BAT/requirements.txt`. `python-Levenshtein` (or `Levenshtein`) is required by the
   `autopipeline` validation; add it if requirements.txt lacks it.
3. **Benchmark data** (not in git, about 16 GB). From the main machine:
   `rsync -a --info=progress2 <user>@<main>:/home/asurite.ad.asu.edu/jrtandel/transchema/autopipeline-benchmarks/github-pipelines/ ~/github-pipelines/`
   Smart-building v2 (needed for `smartbuilding`/`both`; includes `split_manifest.csv`):
   `rsync -a --info=progress2 <user>@<main>:/home/asurite.ad.asu.edu/jrtandel/transchema/autopipeline-benchmarks/smartbuilding-pipelines-v2-split/ ~/smartbuilding-pipelines-v2-split/`
   BAT itself only reads `target.csv` and `test_*.csv` in each `length<L>_<id>` folder; the evaluator may read
   more, so copy the whole folder unless you have checked that.
4. **SSH tunnel to the DMX proxy**, left running in its own terminal or `tmux`:
   `ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>`
   Check: `curl -s -m 5 -o /dev/null -w '%{http_code}\n' -X POST http://localhost:8000/v1/chat/completions`
   should print a number such as 400 or 404, not `000`. The launcher refuses to start otherwise.

## Run

```bash
cd transchema/BAT
export GITHUB_BASE_PATH=~/github-pipelines SB_BASE_PATH=~/smartbuilding-pipelines-v2-split VENV=~/bat_env
tmux new -s bat
bash run_bat_target_examples.sh flash        # or: pro / oss120b
```

Quick smoke test first: `CASES_OVERRIDE="1_1" bash run_bat_target_examples.sh flash smartbuilding` (or `1_0 1_1` with `github`).

To confirm the examples reach the prompts, after a case starts:
`grep -A8 "Target Table" logs/github_<model>_<TS>/llm/*.jsonl | head -20` shows a `**Rows:**` block under the target columns.

## Output

- Results: `BAT/result/github-pipelines/<model>/execution_<TS>/` and `BAT/result/smart_building_v2/<model>/execution_<TS>/`
- Scores: `BAT/predict/{github-pipelines,smart_building_v2}/<model>/execution_<TS>/g<L>_c<id>/master_results_*.csv`
- Logs: GitHub `BAT/logs/github_<model>_<TS>/` (`cases/` per-case logs, `llm/` per-call prompts and tokens); smart building `BAT/logs/smartbuilding_v2_parallel_<TS>/` (per-case) and `BAT/logs/smartbuilding_v2_llm_<model>_<TS>/`.
- Each benchmark ends by printing `BAT <model>, github-pipelines: N/698` and `BAT <model>, smart_building_v2: N/105`.

## Notes

- Each case is killed after `CASE_TIMEOUT` (600 s) and counts as unscored; the run continues.
- If the tunnel drops, cases fail fast with connection errors; restart the tunnel and re-run only the missing
  ones with `CASES_OVERRIDE="4_0 9_17 ..."` (space-separated `<length>_<id>`).
- Different machines can write the same repo paths, so do not rsync result folders back into one tree
  without keeping the `<model>` directory level.
