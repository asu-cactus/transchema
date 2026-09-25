#!/bin/bash
# Reward-function ablation (Ablation Plan §1): "w/o s_rows+s_missing" and "w/o s_cred"
# rows, on dmx-gpt-oss-120b. The other half of the 4-row batch (w/o s_fd and w/o s_col
# run on a separate machine in parallel -- see run_ablation_reward_wofd_wocol.sh).
#
# Order: ALL of GitHub first (both configs), THEN all of Smart Building (both configs):
#   1. GitHub,        w/o s_rows+s_missing (698 cases)
#   2. GitHub,        w/o s_cred           (698 cases)
#   3. Smart Building, w/o s_rows+s_missing (105 cases, full benchmark -- not the 20-case pilot)
#   4. Smart Building, w/o s_cred           (105 cases, full benchmark)
#
# Single pass per case: SAME_LEAF_STOPPING=0 (no early leaf stopping), full budget of
# --mcts_iterations 40 / --case_timeout 600s, MAX_JOBS=20. No 2-phase retry pass.
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_ablation_reward_rowsmissing_wocred.sh
#
# Overrides:
#     MAX_JOBS=20        CASE_TIMEOUT=600      MIN_FREE_GB=15
#     RUN_TAG_PREFIX=abl default; result/log dirs are github_${RUN_TAG_PREFIX}_worowsmiss_<model>
#                        etc. -- see run_github_mcts_dmx.sh / run_smartbuilding_v2_mcts20_dmx.sh
#     DRY_RUN=1          print each stage's case list / counts and exit (no LLM calls)

cd "$(dirname "$0")" || exit 1

MODEL="dmx-gpt-oss-120b"
MAX_JOBS="${MAX_JOBS:-20}"
CASE_TIMEOUT="${CASE_TIMEOUT:-600}"
MIN_FREE_GB="${MIN_FREE_GB:-15}"
RUN_TAG_PREFIX="${RUN_TAG_PREFIX:-abl}"
SB_LENGTHS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"   # full 105-case Smart Building benchmark

log() { echo "[$(date '+%H:%M:%S')] [BATCH] $1"; }

t0=$(date +%s)

log "===== 1/4: GitHub, w/o s_rows+s_missing (drop row_count_score,max_missing_score) ====="
DROP_SCORE_COMPONENTS="row_count_score,max_missing_score" SAME_LEAF_STOPPING=0 RUN_TAG="${RUN_TAG_PREFIX}_worowsmiss" \
    MODELS="$MODEL" MAX_JOBS="$MAX_JOBS" CASE_TIMEOUT="$CASE_TIMEOUT" MIN_FREE_GB="$MIN_FREE_GB" \
    DRY_RUN="${DRY_RUN:-}" \
    bash run_github_mcts_dmx.sh || { log "GitHub w/o s_rows+s_missing FAILED -- stopping the batch"; exit 1; }

log "===== 2/4: GitHub, w/o s_cred (drop credibility_weight) ====="
DROP_SCORE_COMPONENTS=credibility_weight SAME_LEAF_STOPPING=0 RUN_TAG="${RUN_TAG_PREFIX}_wocred" \
    MODELS="$MODEL" MAX_JOBS="$MAX_JOBS" CASE_TIMEOUT="$CASE_TIMEOUT" MIN_FREE_GB="$MIN_FREE_GB" \
    DRY_RUN="${DRY_RUN:-}" \
    bash run_github_mcts_dmx.sh || { log "GitHub w/o s_cred FAILED -- stopping the batch"; exit 1; }

log "===== 3/4: Smart Building (full 105), w/o s_rows+s_missing ====="
DROP_SCORE_COMPONENTS="row_count_score,max_missing_score" SAME_LEAF_STOPPING=0 RUN_TAG="${RUN_TAG_PREFIX}_worowsmiss" \
    MODELS="$MODEL" MAX_JOBS="$MAX_JOBS" CASE_TIMEOUT="$CASE_TIMEOUT" MIN_FREE_GB="$MIN_FREE_GB" \
    LENGTHS="$SB_LENGTHS" DRY_RUN="${DRY_RUN:-}" \
    bash run_smartbuilding_v2_mcts20_dmx.sh || { log "Smart Building w/o s_rows+s_missing FAILED -- stopping the batch"; exit 1; }

log "===== 4/4: Smart Building (full 105), w/o s_cred ====="
DROP_SCORE_COMPONENTS=credibility_weight SAME_LEAF_STOPPING=0 RUN_TAG="${RUN_TAG_PREFIX}_wocred" \
    MODELS="$MODEL" MAX_JOBS="$MAX_JOBS" CASE_TIMEOUT="$CASE_TIMEOUT" MIN_FREE_GB="$MIN_FREE_GB" \
    LENGTHS="$SB_LENGTHS" DRY_RUN="${DRY_RUN:-}" \
    bash run_smartbuilding_v2_mcts20_dmx.sh || { log "Smart Building w/o s_cred FAILED -- stopping the batch"; exit 1; }

log "ALL 4 STAGES COMPLETE in $(( ($(date +%s)-t0)/60 )) min"
