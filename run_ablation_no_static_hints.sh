#!/bin/bash
# No-static-hints ablation (Ablation Plan §4/§9-adjacent -- prompt-context family): disable
# the 20-30ish fixed rule-text hints (hints/hints_static.py's HINTS dict, injected via
# --no_static_hints) while leaving everything else at production defaults: RAG ON
# (curated_pipeline, default), det_score_value reward, two-phase (leafstop then no-leafstop
# retry of phase-1 failures -- the "2 pass system"). dmx-gpt-oss-120b, GitHub + Smart Building.
#
# What --no_static_hints actually removes (see commit 302e8624 for the full investigation and
# a real bug fix that was required first): JOIN_HINT_IDS, GROUPBY_HINT_IDS, AGGREGATE_HINT_IDS,
# NEXT_OPERATOR_HINT_IDS at the expand step (every tree node); PIPELINE_HINT_IDS at
# simulate/script-gen; CRITIQUE_HINT_IDS at critique. On Smart Building, also removes the
# SmartBuilding-specific ~60-line index_col/date-formatting override block (it's static-hints-
# gated too). What SURVIVES regardless (not touched by this flag, by design): RAG hints,
# hint_v3's dynamic FD-mining-derived JOIN/GROUP_BY candidates (the "[hints_v3 JOIN]"/
# "[hints_v3 GROUP BY]" log lines), aggregation evidence, and anything hint_source/fd_flag-gated
# (both already off by default).
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_ablation_no_static_hints.sh
# Overrides: MAX_JOBS  GH_MAX_JOBS  SB_MAX_JOBS  RUN_TAG_PREFIX  DRY_RUN=1  ALLOW_NO_MEMORY_GUARD=1

cd "$(dirname "$0")" || exit 1

MODEL="dmx-gpt-oss-120b"
MAX_JOBS="${MAX_JOBS:-30}"
GH_MAX_JOBS="${GH_MAX_JOBS:-$MAX_JOBS}"
SB_MAX_JOBS="${SB_MAX_JOBS:-$MAX_JOBS}"
RUN_TAG_PREFIX="${RUN_TAG_PREFIX:-abl_nostatic}"
SB_LENGTHS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"
export NO_STATIC_HINTS=1

log() { echo "[$(date '+%H:%M:%S')] [BATCH] $1"; }

# Host protection: same memory ceiling as the other ablation batches. Refuses to start without it.
if [ -z "${DRY_RUN:-}" ]; then
    if ! bash memory_guard.sh on; then
        if [ -n "${ALLOW_NO_MEMORY_GUARD:-}" ]; then log "WARNING: running WITHOUT the memory guard (ALLOW_NO_MEMORY_GUARD=1)"
        else log "memory guard unavailable -- refusing to start (set ALLOW_NO_MEMORY_GUARD=1 to override)"; exit 1; fi
    fi
fi

t0=$(date +%s)

log "===== 1/2: GitHub, no static hints (RAG on, two-phase) ====="
RUN_TAG="${RUN_TAG_PREFIX}_gh" MODEL="$MODEL" MAX_JOBS="$GH_MAX_JOBS" SKIP_GUARD_PHASE1=1 DRY_RUN="${DRY_RUN:-}" \
    bash run_github_mcts_2phase.sh || { log "GitHub FAILED -- stopping the batch"; exit 1; }

log "===== 2/2: Smart Building (full 105), no static hints (RAG on, two-phase) ====="
MODELS="$MODEL" RUN_TAG="${RUN_TAG_PREFIX}_sb" MAX_JOBS="$SB_MAX_JOBS" LENGTHS="$SB_LENGTHS" \
    SKIP_GUARD_PHASE1=1 DRY_RUN="${DRY_RUN:-}" \
    bash run_smartbuilding_v2_2phase_leafstop.sh || { log "Smart Building FAILED -- stopping the batch"; exit 1; }

log "ALL 2 STAGES COMPLETE in $(( ($(date +%s)-t0)/60 )) min"
