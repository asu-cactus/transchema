#!/bin/bash
# Sample: alternate baselines, dmx-gpt-oss-120b, GitHub-pipelines, all 698 cases.
# Run from the repo root: bash running_scripts/alternate_baselines_github_oss120b_example.sh
#
# Runs all three arms, one after another (never in parallel -- they share the same
# benchmark case folders and each wipes its scratch files at case start):
#   coocrit   CoO + Critique   generation + 1 mcts_style critique round
#   cooreact  CoO + ReAct      materialization + 1 critique round  -> "Operator-Driven ReAct"
#   cotreact  CoT + ReAct      up to 40 critique rounds, no early stopping -> "Pipeline-Driven
#                               ReAct" (also gives Chain-of-Thoughts / CoT+Critique as sub-tiers)
# MAX_JOBS=15 (lower than TreeMorpher/BAT's 20 -- these arms are more failure-sensitive under
# heavy concurrency). See alternate_baselines/run_gh_arms_dmx.sh's header for overrides
# (MODELS, ARMS, LENGTHS, ROUNDS, RULE_HINTS=1, CASES_OVERRIDE, DRY_RUN=1).

cd "$(dirname "$0")/.." || exit 1

MODELS=dmx-gpt-oss-120b MAX_JOBS=15 bash alternate_baselines/run_gh_arms_dmx.sh
