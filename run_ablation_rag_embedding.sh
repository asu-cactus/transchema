#!/bin/bash
# Retrieval-strategy ablation (Ablation Plan §2), embedding-based configs: embedding_only and
# prefix_embedding, on dmx-gpt-oss-120b. This machine's half of the 4-config RAG-strategy sweep
# -- feature_only and prefix_only run on 10.218.105.162 (run_ablation_rag_prefix.sh there), since
# those two never touch the text-embedding model or the embedding_vector column and so need no
# RAG-asset copy at all, only a git pull.
#
# Two-phase per (config, benchmark), same pattern as the lambda/critique-threshold ablations:
# leaf-stopping ON (same_leaf_stopping=5, every case) then leaf-stopping OFF (same_leaf_stopping=0,
# retrying only whatever phase 1 got wrong) -- run_github_mcts_2phase.sh /
# run_smartbuilding_v2_2phase_leafstop.sh.
#
# Order: embedding_only GH, embedding_only SB, prefix_embedding GH, prefix_embedding SB.
#
# Queued behind the currently-running no-RAG batch (run_ablation_no_rag.sh, tmux session
# ablation_no_rag): waits for logs_langraph/ablation_no_rag_batch.log to show "ALL 2 STAGES
# COMPLETE" before starting. Set SKIP_WAIT=1 to start immediately regardless.
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_ablation_rag_embedding.sh
# Overrides: MAX_JOBS  GH_MAX_JOBS  SB_MAX_JOBS  RUN_TAG_PREFIX  DRY_RUN=1  ALLOW_NO_MEMORY_GUARD=1  SKIP_WAIT=1
#
# RAG=curated_pipeline is held constant; CURATED_RETRIEVAL_MODE (mcts_search.py's
# --curated_retrieval_mode) is exported per stage -- both env vars the two-phase launchers already
# pass through untouched (same mechanism as TREEMORPHER_EXPAND_LAMBDA / _CRITIQUE_THRESHOLD).
#
# Prerequisite (already done on this machine as of 2026-09-28): rag_pipeline/db/curated_pipeline_656.db
# must have its embedding_vector column backfilled -- see rag_pipeline/add_curated_pipeline_embeddings.py.
# Also requires torch/torchvision to actually import (torchvision was pinned to 0.19.1 in
# requirements.txt to match torch==2.4.1 -- the previously-installed 0.21.0 crashed on import,
# which had been silently disabling --rag global too; see get_rag_hints()/mcts_search.py history).
#
# RESUME NOTE (same as the lambda/critique-threshold sweeps): GitHub stages resume cleanly. Smart
# Building stages do NOT -- run_smartbuilding_v2_2phase_leafstop.sh always appends a fresh
# timestamp to RUN_TAG, so a relaunch mid-SB-stage restarts that stage's own progress from scratch.

cd "$(dirname "$0")" || exit 1

MODEL="dmx-gpt-oss-120b"
MAX_JOBS="${MAX_JOBS:-30}"
GH_MAX_JOBS="${GH_MAX_JOBS:-$MAX_JOBS}"
SB_MAX_JOBS="${SB_MAX_JOBS:-$MAX_JOBS}"
RUN_TAG_PREFIX="${RUN_TAG_PREFIX:-abl_rag_emb}"
SB_LENGTHS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"

log() { echo "[$(date '+%H:%M:%S')] [BATCH] $1"; }

NO_RAG_LOG="logs_langraph/ablation_no_rag_batch.log"
if [ -z "${SKIP_WAIT:-}" ] && [ -z "${DRY_RUN:-}" ]; then
    if ! grep -q "ALL 2 STAGES COMPLETE" "$NO_RAG_LOG" 2>/dev/null; then
        log "Waiting for the no-RAG batch ($NO_RAG_LOG) to finish first (SKIP_WAIT=1 to skip)..."
        while ! grep -q "ALL 2 STAGES COMPLETE" "$NO_RAG_LOG" 2>/dev/null; do sleep 60; done
        log "no-RAG batch complete -- starting."
    fi
fi

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

log "===== 1/4: GitHub, embedding_only ====="
run_gh _embonly embedding_only
log "===== 2/4: Smart Building, embedding_only ====="
run_sb _embonly embedding_only

log "===== 3/4: GitHub, prefix_embedding ====="
run_gh _prefemb prefix_embedding
log "===== 4/4: Smart Building, prefix_embedding ====="
run_sb _prefemb prefix_embedding

log "ALL 4 STAGES COMPLETE in $(( ($(date +%s)-t0)/60 )) min"
