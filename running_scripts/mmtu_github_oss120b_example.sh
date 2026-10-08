#!/bin/bash
# Sample: MMTU, dmx-gpt-oss-120b, GitHub-pipelines (MMTU's own 672-of-698 coverage).
# Run from the repo root: bash running_scripts/mmtu_github_oss120b_example.sh
#
# One-shot Transform-by-output-target-schema baseline -- a single LLM call per case,
# no search/critique. See run_mmtu_github_dmx.sh's header for overrides (N_PARALLEL,
# LENGTH, EVAL_ONLY=1 to re-score without re-querying, DRY_RUN=1).

cd "$(dirname "$0")/.." || exit 1

MODEL=dmx-gpt-oss-120b N_PARALLEL=15 bash run_mmtu_github_dmx.sh
