#!/bin/bash
# Expansion-policy ablation (Ablation Plan §3): lambda sweep, lambda = 0.25 and 0.75.
# (lambda = 0.5 is the shipped default -- already covered by the main experiment numbers, not
# re-run here.) dmx-gpt-oss-120b, two-phase per (lambda, benchmark): leaf-stopping ON
# (same_leaf_stopping=5, every case) then leaf-stopping OFF (same_leaf_stopping=0, retrying
# only whatever phase 1 got wrong) -- this is exactly run_github_mcts_2phase.sh /
# run_smartbuilding_v2_2phase_leafstop.sh, which already implement that pairing and already
# skip finished cases on a resume. This script only adds: the lambda override, sequencing all
# 4 stages, MAX_JOBS=30, and the memory guard.
#
# Order: lambda=0.25 GitHub, lambda=0.25 Smart Building, lambda=0.75 GitHub, lambda=0.75 Smart Building.
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_ablation_lambda_sweep.sh
# Overrides: MAX_JOBS  GH_MAX_JOBS  SB_MAX_JOBS  CASE_TIMEOUT  RUN_TAG_PREFIX  DRY_RUN=1  ALLOW_NO_MEMORY_GUARD=1
#
# TREEMORPHER_EXPAND_LAMBDA (Langraph/nodes.py's _OPERATOR_CONFIG_LAMBDA) is an env var the two-phase
# launchers don't touch, so exporting it here before calling them is enough -- no launcher edits needed.
#
# RESUME NOTE: GitHub stages resume cleanly (run_github_mcts_2phase.sh reuses the RUN_TAG this script
# passes it; the underlying launcher skips cases that already have a result). Smart Building stages do
# NOT: run_smartbuilding_v2_2phase_leafstop.sh always appends a fresh timestamp to RUN_TAG by design (see
# its own header), so a relaunch mid-SB-stage restarts that stage's own progress from scratch -- bounded
# to at most one SB stage's worth of redone work, not the whole sweep.

cd "$(dirname "$0")" || exit 1

MODEL="dmx-gpt-oss-120b"
MAX_JOBS="${MAX_JOBS:-30}"
GH_MAX_JOBS="${GH_MAX_JOBS:-$MAX_JOBS}"
SB_MAX_JOBS="${SB_MAX_JOBS:-$MAX_JOBS}"
CASE_TIMEOUT="${CASE_TIMEOUT:-600}"
RUN_TAG_PREFIX="${RUN_TAG_PREFIX:-abl_lambda}"
SB_LENGTHS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"

log() { echo "[$(date '+%H:%M:%S')] [BATCH] $1"; }

# Host protection: a memory ceiling around ALL case scopes together, so a runaway case gets
# killed by the kernel instead of the whole machine stalling under swap thrashing (systemd-oomd
# killing the whole batch was the failure mode seen on the reward-ablation runs; see
# memory_guard.sh's own header). Refuses to start without it, same as run_ablation_reward_wofd_wocol.sh.
if [ -z "${DRY_RUN:-}" ]; then
    if ! bash memory_guard.sh on; then
        if [ -n "${ALLOW_NO_MEMORY_GUARD:-}" ]; then log "WARNING: running WITHOUT the memory guard (ALLOW_NO_MEMORY_GUARD=1)"
        else log "memory guard unavailable -- refusing to start (set ALLOW_NO_MEMORY_GUARD=1 to override)"; exit 1; fi
    fi
fi

t0=$(date +%s)

run_lambda_gh() {   # $1 = lambda, $2 = run-tag suffix
    log "GitHub, lambda=$1 (two-phase: leafstop then noleafstop retry of failures)"
    export TREEMORPHER_EXPAND_LAMBDA="$1"
    # SKIP_GUARD_PHASE1=1: stages run back-to-back, so the previous stage's orphaned scoring
    # subprocesses can still be alive when this one's phase 1 starts (phase 2 always bypasses the
    # guard already). Without this the batch died mid-sweep every time -- see the 2026-09-27 postmortem.
    RUN_TAG="${RUN_TAG_PREFIX}${2}_gh" MODEL="$MODEL" MAX_JOBS="$GH_MAX_JOBS" SKIP_GUARD_PHASE1=1 DRY_RUN="${DRY_RUN:-}" \
        bash run_github_mcts_2phase.sh || { log "GitHub lambda=$1 FAILED -- stopping the batch"; exit 1; }
    unset TREEMORPHER_EXPAND_LAMBDA
}
run_lambda_sb() {   # $1 = lambda, $2 = run-tag suffix
    log "Smart Building (full 105), lambda=$1 (two-phase: leafstop then noleafstop retry of failures)"
    export TREEMORPHER_EXPAND_LAMBDA="$1"
    MODELS="$MODEL" RUN_TAG="${RUN_TAG_PREFIX}${2}_sb" MAX_JOBS="$SB_MAX_JOBS" LENGTHS="$SB_LENGTHS" \
        SKIP_GUARD_PHASE1=1 DRY_RUN="${DRY_RUN:-}" \
        bash run_smartbuilding_v2_2phase_leafstop.sh || { log "Smart Building lambda=$1 FAILED -- stopping the batch"; exit 1; }
    unset TREEMORPHER_EXPAND_LAMBDA
}

log "===== 1/4: GitHub, lambda=0.25 ====="
run_lambda_gh 0.25 _025

log "===== 2/4: Smart Building, lambda=0.25 ====="
run_lambda_sb 0.25 _025

log "===== 3/4: GitHub, lambda=0.75 ====="
run_lambda_gh 0.75 _075

log "===== 4/4: Smart Building, lambda=0.75 ====="
run_lambda_sb 0.75 _075

log "ALL 4 STAGES COMPLETE in $(( ($(date +%s)-t0)/60 )) min"
