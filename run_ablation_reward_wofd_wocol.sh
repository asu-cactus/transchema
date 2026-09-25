#!/bin/bash
# Reward-function ablation (Ablation Plan §1): "w/o s_fd" and "w/o s_col" rows, on
# dmx-gpt-oss-120b. This machine's half of the 4-row batch (the other 2 rows, "w/o
# s_rows+s_missing" and "w/o s_cred", run on a separate machine in parallel).
#
# Order: ALL of GitHub first (both configs), THEN all of Smart Building (both configs):
#   1. GitHub,        w/o s_fd   (698 cases)
#   2. GitHub,        w/o s_col  (698 cases)
#   3. Smart Building, w/o s_fd  (105 cases, full benchmark -- not just the 20-case pilot)
#   4. Smart Building, w/o s_col (105 cases, full benchmark)
#
# Single pass per case: SAME_LEAF_STOPPING=0 (no early leaf stopping), full budget of
# --mcts_iterations 40 / --case_timeout 600s, MAX_JOBS=20. No 2-phase retry pass.
#
# GitHub length-4 cases 0-17 are skipped in both GitHub stages (SKIP_CASES below) -- known
# memory-heavy cases (run_github_mcts_dmx.sh's own header: "L4 at 20 jobs exhausted 62 GB of
# RAM"), and the two crashes during this batch's first two attempts both happened partway
# through L4. NOT applied to Smart Building: its length4 case ids are only 1-10, so reusing
# the same skip list there would silently drop ALL of its length-4 cases instead of none.
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_ablation_reward_wofd_wocol.sh
#
# Overrides:
#     MAX_JOBS=20        CASE_TIMEOUT=600      MIN_FREE_GB=15
#     RUN_TAG_PREFIX=abl default; result/log dirs are github_${RUN_TAG_PREFIX}_wofd_<model>
#                        etc. -- see run_github_mcts_dmx.sh / run_smartbuilding_v2_mcts20_dmx.sh
#     GH_SKIP_CASES      GitHub-only case exclusion, default "4_0".."4_17" (see above)
#     DRY_RUN=1          print each stage's case list / counts and exit (no LLM calls)

cd "$(dirname "$0")" || exit 1

MODEL="dmx-gpt-oss-120b"
MAX_JOBS="${MAX_JOBS:-20}"
CASE_TIMEOUT="${CASE_TIMEOUT:-600}"
MIN_FREE_GB="${MIN_FREE_GB:-15}"
RUN_TAG_PREFIX="${RUN_TAG_PREFIX:-abl}"
SB_LENGTHS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"   # full 105-case Smart Building benchmark
GH_SKIP_CASES="${GH_SKIP_CASES:-4_0 4_1 4_2 4_3 4_4 4_5 4_6 4_7 4_8 4_9 4_10 4_11 4_12 4_13 4_14 4_15 4_16 4_17}"

log() { echo "[$(date '+%H:%M:%S')] [BATCH] $1"; }

t0=$(date +%s)

log "===== 1/4: GitHub, w/o s_fd (drop fd_f1) -- skipping L4 cases 0-17 ====="
DROP_SCORE_COMPONENTS=fd_f1 SAME_LEAF_STOPPING=0 RUN_TAG="${RUN_TAG_PREFIX}_wofd" \
    MODELS="$MODEL" MAX_JOBS="$MAX_JOBS" CASE_TIMEOUT="$CASE_TIMEOUT" MIN_FREE_GB="$MIN_FREE_GB" \
    SKIP_CASES="$GH_SKIP_CASES" DRY_RUN="${DRY_RUN:-}" \
    bash run_github_mcts_dmx.sh || { log "GitHub w/o s_fd FAILED -- stopping the batch"; exit 1; }

log "===== 2/4: GitHub, w/o s_col (drop avg_col_score_1) -- skipping L4 cases 0-17 ====="
DROP_SCORE_COMPONENTS=avg_col_score_1 SAME_LEAF_STOPPING=0 RUN_TAG="${RUN_TAG_PREFIX}_wocol" \
    MODELS="$MODEL" MAX_JOBS="$MAX_JOBS" CASE_TIMEOUT="$CASE_TIMEOUT" MIN_FREE_GB="$MIN_FREE_GB" \
    SKIP_CASES="$GH_SKIP_CASES" DRY_RUN="${DRY_RUN:-}" \
    bash run_github_mcts_dmx.sh || { log "GitHub w/o s_col FAILED -- stopping the batch"; exit 1; }

log "===== 3/4: Smart Building (full 105), w/o s_fd (drop fd_f1) ====="
DROP_SCORE_COMPONENTS=fd_f1 SAME_LEAF_STOPPING=0 RUN_TAG="${RUN_TAG_PREFIX}_wofd" \
    MODELS="$MODEL" MAX_JOBS="$MAX_JOBS" CASE_TIMEOUT="$CASE_TIMEOUT" MIN_FREE_GB="$MIN_FREE_GB" \
    LENGTHS="$SB_LENGTHS" DRY_RUN="${DRY_RUN:-}" \
    bash run_smartbuilding_v2_mcts20_dmx.sh || { log "Smart Building w/o s_fd FAILED -- stopping the batch"; exit 1; }

log "===== 4/4: Smart Building (full 105), w/o s_col (drop avg_col_score_1) ====="
DROP_SCORE_COMPONENTS=avg_col_score_1 SAME_LEAF_STOPPING=0 RUN_TAG="${RUN_TAG_PREFIX}_wocol" \
    MODELS="$MODEL" MAX_JOBS="$MAX_JOBS" CASE_TIMEOUT="$CASE_TIMEOUT" MIN_FREE_GB="$MIN_FREE_GB" \
    LENGTHS="$SB_LENGTHS" DRY_RUN="${DRY_RUN:-}" \
    bash run_smartbuilding_v2_mcts20_dmx.sh || { log "Smart Building w/o s_col FAILED -- stopping the batch"; exit 1; }

log "ALL 4 STAGES COMPLETE in $(( ($(date +%s)-t0)/60 )) min"
