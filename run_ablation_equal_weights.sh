#!/bin/bash
# Weight-tuning ablation (Ablation Plan D5, "no weight tuning" condition): SCORE_WEIGHTS=equal
# -- DEFAULT_SCORE_1_WEIGHTS (1/6 each across all 6 score_1 components) AND
# EQUAL_COLUMN_TYPE_WEIGHTS (nested per-column-type term weights, e.g. float's js/range 1:1
# instead of the learned/original 2:1) -- see eval_score_value_based.py and the 87e227dc commit
# for the full writeup. Everything else at production defaults: RAG ON (curated_pipeline),
# det_score_value reward, static hints ON, two-phase (leafstop then no-leafstop retry of
# phase-1 failures -- the "2 pass system"). dmx-gpt-oss-120b, GitHub + Smart Building.
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_ablation_equal_weights.sh
# Overrides: MAX_JOBS  GH_MAX_JOBS  SB_MAX_JOBS  RUN_TAG_PREFIX  DRY_RUN=1  ALLOW_NO_MEMORY_GUARD=1

cd "$(dirname "$0")" || exit 1

MODEL="dmx-gpt-oss-120b"
MAX_JOBS="${MAX_JOBS:-30}"
GH_MAX_JOBS="${GH_MAX_JOBS:-$MAX_JOBS}"
SB_MAX_JOBS="${SB_MAX_JOBS:-$MAX_JOBS}"
RUN_TAG_PREFIX="${RUN_TAG_PREFIX:-abl_eqweight}"
SB_LENGTHS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"
export SCORE_WEIGHTS=equal

log() { echo "[$(date '+%H:%M:%S')] [BATCH] $1"; }

# Host protection: same memory ceiling as the other ablation batches. Refuses to start without it.
if [ -z "${DRY_RUN:-}" ]; then
    if ! bash memory_guard.sh on; then
        if [ -n "${ALLOW_NO_MEMORY_GUARD:-}" ]; then log "WARNING: running WITHOUT the memory guard (ALLOW_NO_MEMORY_GUARD=1)"
        else log "memory guard unavailable -- refusing to start (set ALLOW_NO_MEMORY_GUARD=1 to override)"; exit 1; fi
    fi
fi

t0=$(date +%s)

log "===== 1/2: GitHub, equal weights (RAG on, static hints on, two-phase) ====="
RUN_TAG="${RUN_TAG_PREFIX}_gh" MODEL="$MODEL" MAX_JOBS="$GH_MAX_JOBS" SKIP_GUARD_PHASE1=1 DRY_RUN="${DRY_RUN:-}" \
    bash run_github_mcts_2phase.sh || { log "GitHub FAILED -- stopping the batch"; exit 1; }

log "===== 2/2: Smart Building (full 105), equal weights (RAG on, static hints on, two-phase) ====="
MODELS="$MODEL" RUN_TAG="${RUN_TAG_PREFIX}_sb" MAX_JOBS="$SB_MAX_JOBS" LENGTHS="$SB_LENGTHS" \
    SKIP_GUARD_PHASE1=1 DRY_RUN="${DRY_RUN:-}" \
    bash run_smartbuilding_v2_2phase_leafstop.sh || { log "Smart Building FAILED -- stopping the batch"; exit 1; }

log "ALL 2 STAGES COMPLETE in $(( ($(date +%s)-t0)/60 )) min"
