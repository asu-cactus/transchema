#!/bin/bash
# Retrieval ablation (Ablation Plan §2): no RAG at all, on dmx-gpt-oss-120b. Baseline for the
# retrieval ablation family -- more RAG configs (e.g. reduced top-k, alternate retrieval modes)
# get added as separate stages/scripts once this one is running.
#
# RAG is controlled by the RAG env var both inner launchers already read:
#   RAG="${RAG-curated_pipeline}"   -- note ${VAR-default}, not ${VAR:-default}: an explicitly
#   empty RAG="" is kept empty (RAG disabled), only a genuinely UNSET var falls back to
#   curated_pipeline. No launcher code changes were needed for this ablation.
#
# Single pass per benchmark (not the two-phase leafstop+retry pattern used for the lambda/
# critique-threshold ablations): one straight run through GitHub (698 cases), then one straight
# run through Smart Building (full 105-case benchmark). same_leaf_stopping left at each
# launcher's own default (5).
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_ablation_no_rag.sh
# Overrides: MAX_JOBS  GH_MAX_JOBS  SB_MAX_JOBS  CASE_TIMEOUT  RUN_TAG_PREFIX  DRY_RUN=1  ALLOW_NO_MEMORY_GUARD=1

cd "$(dirname "$0")" || exit 1

MODEL="dmx-gpt-oss-120b"
MAX_JOBS="${MAX_JOBS:-30}"
GH_MAX_JOBS="${GH_MAX_JOBS:-$MAX_JOBS}"
SB_MAX_JOBS="${SB_MAX_JOBS:-$MAX_JOBS}"
CASE_TIMEOUT="${CASE_TIMEOUT:-600}"
RUN_TAG_PREFIX="${RUN_TAG_PREFIX:-abl_norag}"
SB_LENGTHS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"

log() { echo "[$(date '+%H:%M:%S')] [BATCH] $1"; }

# Host protection: same memory ceiling as the other ablation batches. Refuses to start without it.
if [ -z "${DRY_RUN:-}" ]; then
    if ! bash memory_guard.sh on; then
        if [ -n "${ALLOW_NO_MEMORY_GUARD:-}" ]; then log "WARNING: running WITHOUT the memory guard (ALLOW_NO_MEMORY_GUARD=1)"
        else log "memory guard unavailable -- refusing to start (set ALLOW_NO_MEMORY_GUARD=1 to override)"; exit 1; fi
    fi
fi

t0=$(date +%s)

log "===== 1/2: GitHub, no RAG ====="
RAG="" RUN_TAG="${RUN_TAG_PREFIX}_gh" MODELS="$MODEL" MAX_JOBS="$GH_MAX_JOBS" CASE_TIMEOUT="$CASE_TIMEOUT" DRY_RUN="${DRY_RUN:-}" \
    bash run_github_mcts_dmx.sh || { log "GitHub no-RAG FAILED -- stopping the batch"; exit 1; }

log "===== 2/2: Smart Building (full 105), no RAG ====="
# SKIP_GUARD=1: stage 2 starts right after stage 1 -- orphaned scoring subprocesses of stage 1's
# last case can still be alive and would otherwise trip the "an MCTS run is already active" check.
RAG="" RUN_TAG="${RUN_TAG_PREFIX}_sb" MODELS="$MODEL" MAX_JOBS="$SB_MAX_JOBS" CASE_TIMEOUT="$CASE_TIMEOUT" \
    LENGTHS="$SB_LENGTHS" SKIP_GUARD=1 DRY_RUN="${DRY_RUN:-}" \
    bash run_smartbuilding_v2_mcts20_dmx.sh || { log "Smart Building no-RAG FAILED -- stopping the batch"; exit 1; }

log "ALL 2 STAGES COMPLETE in $(( ($(date +%s)-t0)/60 )) min"
