#!/bin/bash
# Critique-invocation ablation (Ablation Plan §5): when to invoke the critique step during
# simulation. dmx-gpt-oss-120b, two-phase per (config, benchmark): leaf-stopping ON
# (same_leaf_stopping=5, every case) then leaf-stopping OFF (same_leaf_stopping=0, retrying
# only whatever phase 1 got wrong) -- run_github_mcts_2phase.sh /
# run_smartbuilding_v2_2phase_leafstop.sh, same as the lambda sweep.
#
# Configs (4): critique threshold tau = 0.9, 0.8, 0.7, and no critique at all.
#   tau=1.0 (critique whenever score < 1.0, i.e. any non-perfect attempt) is the EXISTING
#   default for reward=det_score_value -- already the strictest possible value, not re-run here.
#   Lowering tau makes critique fire less often (only on attempts scoring below tau).
#   "No critique" = --mcts_critique_mode none (an existing flag, no threshold involved at all).
#
# Order: tau=0.9 GH, tau=0.9 SB, tau=0.8 GH, tau=0.8 SB, tau=0.7 GH, tau=0.7 SB,
#        no-critique GH, no-critique SB.
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_ablation_critique_threshold.sh
# Overrides: MAX_JOBS  GH_MAX_JOBS  SB_MAX_JOBS  CASE_TIMEOUT  RUN_TAG_PREFIX  DRY_RUN=1  ALLOW_NO_MEMORY_GUARD=1
#
# TREEMORPHER_CRITIQUE_THRESHOLD (Langraph/nodes.py's should_critique) is an env var the
# two-phase launchers don't touch, so exporting it here before calling them is enough -- no
# launcher edits needed. Same mechanism as TREEMORPHER_EXPAND_LAMBDA for the lambda sweep.
# The no-critique config does NOT set this var at all -- it uses --mcts_critique_mode none
# instead, via MCTS_CRITIQUE_MODE below, which the launchers DO forward as --mcts_critique_mode.
#
# RESUME NOTE (same as the lambda sweep): GitHub stages resume cleanly on a relaunch. Smart
# Building stages do NOT -- run_smartbuilding_v2_2phase_leafstop.sh always appends a fresh
# timestamp to RUN_TAG by design, so a relaunch mid-SB-stage restarts that stage's own
# progress from scratch, bounded to one stage's worth of redone work.

cd "$(dirname "$0")" || exit 1

MODEL="dmx-gpt-oss-120b"
MAX_JOBS="${MAX_JOBS:-30}"
GH_MAX_JOBS="${GH_MAX_JOBS:-$MAX_JOBS}"
SB_MAX_JOBS="${SB_MAX_JOBS:-$MAX_JOBS}"
CASE_TIMEOUT="${CASE_TIMEOUT:-600}"
RUN_TAG_PREFIX="${RUN_TAG_PREFIX:-abl_crit}"
SB_LENGTHS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"

log() { echo "[$(date '+%H:%M:%S')] [BATCH] $1"; }

# Host protection: same memory ceiling as the lambda sweep. Refuses to start without it.
if [ -z "${DRY_RUN:-}" ]; then
    if ! bash memory_guard.sh on; then
        if [ -n "${ALLOW_NO_MEMORY_GUARD:-}" ]; then log "WARNING: running WITHOUT the memory guard (ALLOW_NO_MEMORY_GUARD=1)"
        else log "memory guard unavailable -- refusing to start (set ALLOW_NO_MEMORY_GUARD=1 to override)"; exit 1; fi
    fi
fi

t0=$(date +%s)

# $1 = human label, $2 = run-tag suffix, $3 = TREEMORPHER_CRITIQUE_THRESHOLD value (empty = unset,
# i.e. use the launchers' own default mcts_critique_mode=simulate behavior at tau=1.0 -- not used
# here since every config below sets either a threshold or --mcts_critique_mode none explicitly),
# $4 = extra args appended verbatim to the inner launcher's own env-var assignments (e.g. to pass
# MCTS_CRITIQUE_MODE=none through to run_github_mcts_dmx.sh's --mcts_critique_mode via that launcher's
# forwarding -- see the two run_lambda_* equivalents below, which set TREEMORPHER_CRITIQUE_THRESHOLD
# and/or MCTS_CRITIQUE_MODE as needed per config).
run_gh() {   # $1 = run-tag suffix, $2 = TREEMORPHER_CRITIQUE_THRESHOLD or "", $3 = MCTS_CRITIQUE_MODE or ""
    if [ -n "$2" ]; then export TREEMORPHER_CRITIQUE_THRESHOLD="$2"; else unset TREEMORPHER_CRITIQUE_THRESHOLD; fi
    if [ -n "$3" ]; then export MCTS_CRITIQUE_MODE="$3"; else unset MCTS_CRITIQUE_MODE; fi
    RUN_TAG="${RUN_TAG_PREFIX}${1}_gh" MODEL="$MODEL" MAX_JOBS="$GH_MAX_JOBS" SKIP_GUARD_PHASE1=1 DRY_RUN="${DRY_RUN:-}" \
        bash run_github_mcts_2phase.sh || { log "GitHub $1 FAILED -- stopping the batch"; exit 1; }
    unset TREEMORPHER_CRITIQUE_THRESHOLD MCTS_CRITIQUE_MODE
}
run_sb() {   # $1 = run-tag suffix, $2 = TREEMORPHER_CRITIQUE_THRESHOLD or "", $3 = MCTS_CRITIQUE_MODE or ""
    if [ -n "$2" ]; then export TREEMORPHER_CRITIQUE_THRESHOLD="$2"; else unset TREEMORPHER_CRITIQUE_THRESHOLD; fi
    if [ -n "$3" ]; then export MCTS_CRITIQUE_MODE="$3"; else unset MCTS_CRITIQUE_MODE; fi
    MODELS="$MODEL" RUN_TAG="${RUN_TAG_PREFIX}${1}_sb" MAX_JOBS="$SB_MAX_JOBS" LENGTHS="$SB_LENGTHS" \
        SKIP_GUARD_PHASE1=1 DRY_RUN="${DRY_RUN:-}" \
        bash run_smartbuilding_v2_2phase_leafstop.sh || { log "Smart Building $1 FAILED -- stopping the batch"; exit 1; }
    unset TREEMORPHER_CRITIQUE_THRESHOLD MCTS_CRITIQUE_MODE
}

log "===== 1/8: GitHub, tau=0.9 ====="
run_gh _tau09 0.9 ""
log "===== 2/8: Smart Building, tau=0.9 ====="
run_sb _tau09 0.9 ""

log "===== 3/8: GitHub, tau=0.8 ====="
run_gh _tau08 0.8 ""
log "===== 4/8: Smart Building, tau=0.8 ====="
run_sb _tau08 0.8 ""

log "===== 5/8: GitHub, tau=0.7 ====="
run_gh _tau07 0.7 ""
log "===== 6/8: Smart Building, tau=0.7 ====="
run_sb _tau07 0.7 ""

log "===== 7/8: GitHub, no critique ====="
run_gh _nocrit "" none
log "===== 8/8: Smart Building, no critique ====="
run_sb _nocrit "" none

log "ALL 8 STAGES COMPLETE in $(( ($(date +%s)-t0)/60 )) min"
