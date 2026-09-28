#!/bin/bash
# Retrieval-strategy ablation (Ablation Plan §2), non-embedding configs: feature_only and
# prefix_only, on dmx-gpt-oss-120b. Runs on this server's existing curated_pipeline_656.db
# unchanged -- feature_only ranks ALL 656 pipelines by the 8-dim structural feature vector
# (already present in every build of that DB), prefix_only prefix-matches then picks randomly.
# Neither mode touches embedding_vector or loads the text-embedding model, so no RAG-asset copy
# or torch/torchvision fix is needed here -- only the code changes (git pull). The other two
# configs (embedding_only, prefix_embedding) run on a different machine
# (run_ablation_rag_embedding.sh), which DOES need the embedding backfill.
#
# Two-phase per (config, benchmark), same pattern as the lambda/critique-threshold ablations:
# leaf-stopping ON (same_leaf_stopping=5, every case) then leaf-stopping OFF (same_leaf_stopping=0,
# retrying only whatever phase 1 got wrong) -- run_github_mcts_2phase.sh /
# run_smartbuilding_v2_2phase_leafstop.sh.
#
# Order: feature_only GH, feature_only SB, prefix_only GH, prefix_only SB.
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_ablation_rag_prefix.sh
# Overrides: MAX_JOBS  GH_MAX_JOBS  SB_MAX_JOBS  RUN_TAG_PREFIX  DRY_RUN=1  ALLOW_NO_MEMORY_GUARD=1
#
# RAG=curated_pipeline is held constant; CURATED_RETRIEVAL_MODE (mcts_search.py's
# --curated_retrieval_mode) is exported per stage -- both env vars the two-phase launchers already
# pass through untouched (same mechanism as TREEMORPHER_EXPAND_LAMBDA / _CRITIQUE_THRESHOLD).
#
# prefix_only picks randomly among prefix-matched examples each call (unseeded) -- this is by
# design (the ablation's whole point is "no similarity ranking, just whatever prefix-matched"),
# not a bug: don't expect byte-identical hints across two runs of the same case.
#
# RESUME NOTE (same as the other ablations): GitHub stages resume cleanly. Smart Building stages
# do NOT -- run_smartbuilding_v2_2phase_leafstop.sh always appends a fresh timestamp to RUN_TAG,
# so a relaunch mid-SB-stage restarts that stage's own progress from scratch.

cd "$(dirname "$0")" || exit 1

MODEL="dmx-gpt-oss-120b"
MAX_JOBS="${MAX_JOBS:-30}"
GH_MAX_JOBS="${GH_MAX_JOBS:-$MAX_JOBS}"
SB_MAX_JOBS="${SB_MAX_JOBS:-$MAX_JOBS}"
RUN_TAG_PREFIX="${RUN_TAG_PREFIX:-abl_rag_pfx}"
SB_LENGTHS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"

log() { echo "[$(date '+%H:%M:%S')] [BATCH] $1"; }

if [ -z "${DRY_RUN:-}" ]; then
    if ! bash memory_guard.sh on; then
        if [ -n "${ALLOW_NO_MEMORY_GUARD:-}" ]; then log "WARNING: running WITHOUT the memory guard (ALLOW_NO_MEMORY_GUARD=1)"
        else log "memory guard unavailable -- refusing to start (set ALLOW_NO_MEMORY_GUARD=1 to override)"; exit 1; fi
    fi
fi

t0=$(date +%s)

run_gh() {   # $1 = run-tag suffix, $2 = CURATED_RETRIEVAL_MODE
    export RAG=curated_pipeline CURATED_RETRIEVAL_MODE="$2"
    RUN_TAG="${RUN_TAG_PREFIX}${1}_gh" MODEL="$MODEL" MAX_JOBS="$GH_MAX_JOBS" SKIP_GUARD_PHASE1=1 DRY_RUN="${DRY_RUN:-}" \
        bash run_github_mcts_2phase.sh || { log "GitHub $1 FAILED -- stopping the batch"; exit 1; }
}
run_sb() {   # $1 = run-tag suffix, $2 = CURATED_RETRIEVAL_MODE
    export RAG=curated_pipeline CURATED_RETRIEVAL_MODE="$2"
    MODELS="$MODEL" RUN_TAG="${RUN_TAG_PREFIX}${1}_sb" MAX_JOBS="$SB_MAX_JOBS" LENGTHS="$SB_LENGTHS" \
        SKIP_GUARD_PHASE1=1 DRY_RUN="${DRY_RUN:-}" \
        bash run_smartbuilding_v2_2phase_leafstop.sh || { log "Smart Building $1 FAILED -- stopping the batch"; exit 1; }
}

log "===== 1/4: GitHub, feature_only ====="
run_gh _featonly feature_only
log "===== 2/4: Smart Building, feature_only ====="
run_sb _featonly feature_only

log "===== 3/4: GitHub, prefix_only ====="
run_gh _prefonly prefix_only
log "===== 4/4: Smart Building, prefix_only ====="
run_sb _prefonly prefix_only

log "ALL 4 STAGES COMPLETE in $(( ($(date +%s)-t0)/60 )) min"
