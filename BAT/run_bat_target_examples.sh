#!/usr/bin/env bash
# BAT (MCTS) on the GitHub-pipelines and/or smart-building v2 benchmarks with N target-table example rows in the prompts,
# one model per machine, through a shared 20-worker queue (see run_github_parallel_dmx.sh).
#
# Usage:  bash run_bat_target_examples.sh <oss120b|flash|pro> [github|smartbuilding|both]   (default both, run one after the other)
#   oss120b -> dmx-gpt-oss-120b   flash -> dmx-deepseek-v4-flash   pro -> dmx-deepseek-v4-pro
#
# Overrides: GITHUB_BASE_PATH=<github-pipelines dir>  SB_BASE_PATH=<smartbuilding-pipelines-v2-split dir>  VENV=<venv dir>  N_WORKERS=20  TARGET_EXAMPLES=3
#            LENGTHS="1 2 3 4 5 6 9"  CASE_TIMEOUT=600  (all forwarded to run_github_parallel_dmx.sh)
# Needs the SSH tunnel to the DMX proxy on localhost:8000 (see BAT_TARGET_EXAMPLES_SERVER_SETUP.md).
set -euo pipefail
cd "$(dirname "$0")"
case "${1:-}" in
    oss120b) MODEL=dmx-gpt-oss-120b ;;
    flash)   MODEL=dmx-deepseek-v4-flash ;;
    pro)     MODEL=dmx-deepseek-v4-pro ;;
    *) echo "usage: bash $0 <oss120b|flash|pro>" >&2; exit 2 ;;
esac
export TARGET_EXAMPLES="${TARGET_EXAMPLES:-3}"
export N_WORKERS="${N_WORKERS:-20}"
BENCH="${2:-both}"
rc=0
if [ "$BENCH" = github ] || [ "$BENCH" = both ]; then
    BASE_PATH="${GITHUB_BASE_PATH:-${BASE_PATH:-}}" bash -c '[ -n "$BASE_PATH" ] || unset BASE_PATH; exec bash run_github_parallel_dmx.sh "$0"' "$MODEL" || rc=1
fi
if [ "$BENCH" = smartbuilding ] || [ "$BENCH" = both ]; then
    BASE_PATH="${SB_BASE_PATH:-}" bash -c '[ -n "$BASE_PATH" ] || unset BASE_PATH; exec bash run_smartbuilding_v2_parallel.sh "$0"' "$MODEL" || rc=1
fi
exit $rc
