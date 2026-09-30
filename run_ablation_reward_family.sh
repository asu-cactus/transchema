#!/bin/bash
# Reward-FUNCTION-FAMILY ablation: swap TreeMorpher's whole reward function for competing
# methods' own reward formulations (bat_reward, ap_reward, llm_confidence -- see
# Langraph/nodes.py's _score_and_validate_output for the exact formulas, and the 51f6a1bd
# commit message for how each was derived/verified). Distinct from the earlier "drop one
# score_1 component" reward ablation (run_ablation_reward_wofd_wocol.sh) -- that ablates
# PIECES of det_score_value; this one ablates the WHOLE reward function.
#
# dmx-gpt-oss-120b. Single pass per (reward, benchmark): same_leaf_stopping=5 (launcher
# default), no retry phase -- matches run_ablation_no_rag.sh's convention, not the two-phase
# (leafstop+retry) pattern used for lambda/critique-threshold/RAG-strategy.
#
# Order: bat_reward GH, bat_reward SB, ap_reward GH, ap_reward SB, llm_confidence GH,
# llm_confidence SB.
#
# ap_reward is NOT on a [0,1] scale like the other modes -- it sums 3 independent [0,1]
# components (FD overlap + key overlap + column-mapping), range [0,3]. Langraph/nodes.py's
# should_critique() and _score_and_validate_output already know this (_AP_REWARD_MAX-scaled
# threshold) -- nothing to configure here, just don't be surprised by "reward=3.0000" in the
# ap_reward logs where every other mode shows "reward=1.0000".
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_ablation_reward_family.sh
# Overrides: MAX_JOBS  GH_MAX_JOBS  SB_MAX_JOBS  CASE_TIMEOUT  RUN_TAG_PREFIX  DRY_RUN=1  ALLOW_NO_MEMORY_GUARD=1

cd "$(dirname "$0")" || exit 1

MODEL="dmx-gpt-oss-120b"
MAX_JOBS="${MAX_JOBS:-30}"
GH_MAX_JOBS="${GH_MAX_JOBS:-$MAX_JOBS}"
SB_MAX_JOBS="${SB_MAX_JOBS:-$MAX_JOBS}"
CASE_TIMEOUT="${CASE_TIMEOUT:-600}"
RUN_TAG_PREFIX="${RUN_TAG_PREFIX:-abl_rewfam}"
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

run_gh() {   # $1 = run-tag suffix, $2 = REWARD value
    REWARD="$2" RUN_TAG="${RUN_TAG_PREFIX}${1}_gh" MODEL="$MODEL" MAX_JOBS="$GH_MAX_JOBS" \
        CASE_TIMEOUT="$CASE_TIMEOUT" SKIP_GUARD=1 DRY_RUN="${DRY_RUN:-}" \
        bash run_github_mcts_dmx.sh || { log "GitHub $1 FAILED -- stopping the batch"; exit 1; }
}
run_sb() {   # $1 = run-tag suffix, $2 = REWARD value
    REWARD="$2" MODELS="$MODEL" RUN_TAG="${RUN_TAG_PREFIX}${1}_sb" MAX_JOBS="$SB_MAX_JOBS" \
        CASE_TIMEOUT="$CASE_TIMEOUT" LENGTHS="$SB_LENGTHS" SKIP_GUARD=1 DRY_RUN="${DRY_RUN:-}" \
        bash run_smartbuilding_v2_mcts20_dmx.sh || { log "Smart Building $1 FAILED -- stopping the batch"; exit 1; }
}

log "===== 1/6: GitHub, bat_reward ====="
run_gh _bat bat_reward
log "===== 2/6: Smart Building, bat_reward ====="
run_sb _bat bat_reward

log "===== 3/6: GitHub, ap_reward ====="
run_gh _ap ap_reward
log "===== 4/6: Smart Building, ap_reward ====="
run_sb _ap ap_reward

log "===== 5/6: GitHub, llm_confidence ====="
run_gh _conf llm_confidence
log "===== 6/6: Smart Building, llm_confidence ====="
run_sb _conf llm_confidence

log "ALL 6 STAGES COMPLETE in $(( ($(date +%s)-t0)/60 )) min"
