#!/bin/bash
# Sample: TreeMorpher (MCTS), dmx-gpt-oss-120b, GitHub-pipelines, both phases.
# Run from the repo root: bash running_scripts/treemorpher_github_oss120b_example.sh
#
# Phase 1: same_leaf_stopping=5 (early leaf stopping on), every case.
# Phase 2: same_leaf_stopping=0 (off), only the cases phase 1 did not solve -- launched
#          automatically by run_github_mcts_2phase.sh once phase 1 finishes.
# RAG (curated_pipeline) is on by default; MAX_JOBS=20 matches the real oss-120b runs.
#
# See run_github_mcts_2phase.sh and run_github_mcts_dmx.sh's own header comments for every
# override (LENGTHS, CASE_TIMEOUT, RUN_TAG, DRY_RUN=1 to preview with no LLM calls, etc.).

cd "$(dirname "$0")/.." || exit 1

MODEL=dmx-gpt-oss-120b MAX_JOBS=20 bash run_github_mcts_2phase.sh
