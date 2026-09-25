#!/bin/bash
# Sample: SQLMorpher (ChatGPT+SQL baseline), dmx-gpt-oss-120b, GitHub-pipelines, all 698 cases.
# Run from the repo root: bash running_scripts/sqlmorpher_github_oss120b_example.sh
#
# 15 parallel workers, each with its own Postgres connection -- safe because every case
# creates/drops uniquely-named tables. Run only ONE SQLMorpher process at a time overall
# (two concurrent runs, even of different models, would drop each other's tables).
# See ChatGPTwithSQLscript/run_github_parallel.sh's header for overrides (N_WORKERS,
# LENGTHS, CASES_OVERRIDE, DRY_RUN=1).

cd "$(dirname "$0")/.." || exit 1

N_WORKERS=15 bash ChatGPTwithSQLscript/run_github_parallel.sh dmx-gpt-oss-120b
