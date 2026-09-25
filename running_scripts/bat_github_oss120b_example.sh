#!/bin/bash
# Sample: BAT, dmx-gpt-oss-120b, GitHub-pipelines, all 698 cases.
# Run from the repo root: bash running_scripts/bat_github_oss120b_example.sh
#
# 20 parallel workers, each with its own predict dir and a hard 10-minute per-case
# timeout (BAT's own MCTS solver has no timeout of its own otherwise).
# See BAT/run_github_parallel_dmx.sh's header for overrides (N_WORKERS, LENGTHS,
# CASE_TIMEOUT, SKIP_CASES, CASES_OVERRIDE, DRY_RUN=1).

cd "$(dirname "$0")/.." || exit 1

N_WORKERS=20 bash BAT/run_github_parallel_dmx.sh dmx-gpt-oss-120b
