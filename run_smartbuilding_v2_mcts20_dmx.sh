#!/bin/bash
# Langraph/mcts_search.py on the same smart_building_v2 20-case pilot used for the
# CoT/CoO comparison (L1 c1-10, L2 c1-10), across the three Azure DMX models.
#
# Arguments copied verbatim from run_smartbuilding_v2_coltransform_failed_retry.sh
# (COMMON_ARGS + MAX_JOBS) -- only --model, the case list, and the log/result dirs
# differ. See that script for what each MCTS setting means.
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal, for dmx-*
#     bash run_smartbuilding_v2_mcts20_dmx.sh
#
# Overrides: MODELS="dmx-deepseek-v4-pro" to run a subset. No SKIP_DONE / resume logic --
# mcts_search.py's own result files aren't checked for completion here, so a rerun
# redoes every case (matches how the reference script behaves).
#     LENGTHS="1 2"                   default = the 20-case pilot. Use
#                                LENGTHS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15" for the full
#                                105-case benchmark (L9-L15 have only 3-4 cases each; ids
#                                without a folder are skipped).
#     DROP_SCORE_COMPONENTS="fd_f1"   reward-function ablation switch (Ablation Plan §1),
#                                forwarded to mcts_search.py's --drop_score_components. See
#                                run_github_mcts_dmx.sh's header for the full explanation.
#
# MODELS RUN ONE AFTER ANOTHER: MCTS writes python_recovered_mcts.py /
# target_multisource_mcts*.csv into the SAME benchmark case folders regardless of which
# model produced them, so two models on the same case at once would clobber each other's
# output mid-run. Within one model's run, MAX_JOBS=8 cases run concurrently (unchanged
# from the reference script -- MCTS is heavier per-case than a single LLM call, so this
# stays lower than the CoT/CoO runners' MAX_JOBS=20).

cd "$(dirname "$0")" || exit 1

if ! python3 -c "import transformers" 2>/dev/null; then
    echo "ERROR: venv not active (transformers missing)." >&2
    echo "  run:  source env/bin/activate" >&2
    exit 1
fi

if pgrep -u "$(id -u)" -f "Langraph/mcts_search\.py|python3 critique_data\.py" >/dev/null; then
    echo "ERROR: an MCTS or critique_data.py run is already active. Both write into the" >&2
    echo "  same benchmark case folders; wait for it to finish first." >&2
    exit 1
fi

MODELS="${MODELS:-dmx-gpt-oss-120b dmx-deepseek-v4-flash dmx-deepseek-v4-pro}"
RUN_TAG="${RUN_TAG:-mcts20_dmx}"
# 300s (the reference script's value) starved most cases to 0-2 of the 40 budgeted
# iterations -- see the 2026-09-17 postmortem on cases 1_3/1_4/2_2/2_5. 600s matches
# CoT/CoO+Critique's timeout so the comparison isn't handicapped by budget alone.
CASE_TIMEOUT="${CASE_TIMEOUT:-600}"
# 2026-09-17 postmortem: every stalled/slow LLM call across the dowfix_t600 run was
# fired while 8-18 OTHER requests were simultaneously in flight (mean concurrency
# 15.2, near-saturating this ceiling almost the whole run) -- see the concurrency
# writeup for that run. Lower MAX_JOBS to reduce how often that saturation is hit.
MAX_JOBS="${MAX_JOBS:-20}"
MIN_FREE_GB="${MIN_FREE_GB:-15}"
# 5 (the reference script's value) stops a case as soon as any single leaf has been
# visited 5 times, well before the 40-iteration budget is used -- for retrying cases
# that failed under that early stop, SAME_LEAF_STOPPING=0 disables it so the search
# runs to the full iteration/timeout budget instead.
SAME_LEAF_STOPPING="${SAME_LEAF_STOPPING:-5}"
# Reward-function ablation switch (Ablation Plan §1): forwarded to mcts_search.py's
# --drop_score_components. Comma-separated score_1 component names to force out of
# the weighted average, e.g. "fd_f1" (w/o s_fd), "avg_col_score_1" (w/o s_col),
# "row_count_score,max_missing_score" (w/o s_rows+s_missing), "credibility_weight"
# (w/o s_cred). Empty (default) = unchanged full reward.
DROP_SCORE_COMPONENTS="${DROP_SCORE_COMPONENTS:-}"
# curated_pipeline RAG is built from github-pipelines, not smart_building_v2, so this is a
# cross-domain corpus here -- see run_smartbuilding_v2_det_score_training_rag.sh's note.
# On by default anyway, to match every GitHub TreeMorpher run and the CoT/CoO/ReAct baselines
# on these SAME v2 cases, which already run with this corpus. RAG="" disables it.
RAG="${RAG-curated_pipeline}"
RAG_DB="rag_pipeline/db/curated_pipeline_656.db"
RAG_STATS="rag_pipeline/db/curated_pipeline_features.norm_stats.json"
if [ "$RAG" = "curated_pipeline" ]; then
    for f in "$RAG_DB" "$RAG_STATS"; do
        [ -s "$f" ] || { echo "ERROR: RAG file missing: $f (not in git -- copy it)" >&2; exit 1; }
    done
fi

log() { echo "[$(date '+%H:%M:%S')] [$1] $2"; }

check_disk() {
    local free_gb
    free_gb=$(df --output=avail -BG / | tail -1 | tr -dc '0-9')
    if [ "$free_gb" -lt "$MIN_FREE_GB" ]; then
        echo "ERROR: only ${free_gb}G free on / (need >= ${MIN_FREE_GB}G)." >&2
        echo "  Override with MIN_FREE_GB=<n> if you've judged the risk acceptable." >&2
        return 1
    fi
    return 0
}
check_disk || exit 1

for m in $MODELS; do
    case "$m" in
        dmx-*)
            code=$(curl -s -m 10 -o /dev/null -w '%{http_code}' -X POST \
                   http://localhost:8000/v1/chat/completions)
            if [ "$code" = "000" ]; then
                echo "ERROR: $m needs the SSH tunnel -- nothing is listening on localhost:8000." >&2
                echo "  run:  ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>" >&2
                exit 1
            fi ;;
    esac
done

# See run_sb105_arms_timing.sh's postmortem comment: dmx-deepseek-* loads the
# DeepSeek-V3 tokenizer via AutoTokenizer.from_pretrained() (llm_models.py's
# dmx_encoding()), which hits huggingface.co over the network unless told not to.
# mcts_search.py builds ONE LLMClient per case (not per iteration, unlike
# critique.py's per-round rebuild), so the worst case here is ~MAX_JOBS=8 concurrent
# loads -- well under the 60-concurrent stress test already run clean with
# HF_HUB_OFFLINE=1 -- but there's no reason not to apply the same proven fix.
if [[ " $MODELS " == *" dmx-deepseek"* ]]; then
    if ! python3 -c "
import os
os.environ.pop('HF_HUB_OFFLINE', None)
from transformers import AutoTokenizer
AutoTokenizer.from_pretrained('deepseek-ai/DeepSeek-V3')
" 2>/tmp/dmx_tokenizer_preflight.log; then
        echo "ERROR: could not load/download the DeepSeek-V3 tokenizer. See /tmp/dmx_tokenizer_preflight.log" >&2
        exit 1
    fi
    export HF_HUB_OFFLINE=1
    log "ALL" "tokenizer cache warm -- HF_HUB_OFFLINE=1 set for the rest of this run"
fi

# LENGTHS default "1 2" = the 20-case CoT/CoO/ReAct pilot (c1-10 each). Set
# LENGTHS="3 4 5 6 7 8 9 10 11 12 13 14 15" for the rest of the 105-case benchmark.
# Ids with no case folder are dropped -- the id space is not contiguous at every
# length (L9-L15 have only 3-4 cases each), matching the CoT/CoO runners' handling.
#
# CASES_OVERRIDE="1_3 2_2 2_3" (space-separated "L_c" tokens, underscore -- matches
# how case ids are reported elsewhere) restricts to just those, e.g. for retrying a
# specific run's failures. Takes priority over LENGTHS.
BENCH_DIR="autopipeline-benchmarks/smartbuilding-pipelines-v2-split"
LENGTHS="${LENGTHS:-1 2}"
CASES=()
if [ -n "${CASES_OVERRIDE:-}" ]; then
    for tok in $CASES_OVERRIDE; do
        CASES+=("${tok/_/:}")
    done
else
    for L in $LENGTHS; do
        for c in $(seq 1 10); do
            [ -d "${BENCH_DIR}/length${L}_${c}" ] && CASES+=("${L}:${c}")
        done
    done
fi

if [ -n "${DRY_RUN:-}" ]; then
    echo "MODELS=$MODELS  RUN_TAG=$RUN_TAG  MAX_JOBS=$MAX_JOBS  same_leaf_stopping=$SAME_LEAF_STOPPING  timeout=${CASE_TIMEOUT}s  rag=${RAG:-none}  drop_score_components=${DROP_SCORE_COMPONENTS:-none}"
    echo "total cases per model: ${#CASES[@]}"
    for L in $LENGTHS; do
        n=0; for u in "${CASES[@]}"; do [ "${u%%:*}" = "$L" ] && n=$((n+1)); done
        echo "  length $L: $n cases"
    done
    exit 0
fi

run_case() {
    local model=$1 group=$2 case_id=$3
    # Resolved relative to Langraph/ by mcts_search.py's _HERE, not the repo root --
    # matches every other run_smartbuilding_v2_*.sh script's convention.
    local result_dir="results_langraph/smartbuilding_v2_${RUN_TAG}_${model}"
    local log_base="logs_langraph/smartbuilding_v2_${RUN_TAG}_${model}"
    local exp_name="smartbuilding_v2_${RUN_TAG}_${model}_g${group}_c${case_id}"
    local tag="${model}_G${group}_C${case_id}"
    local stdout_log="${log_base}/stdout_g${group}_c${case_id}.log"
    local case_log_dir="${log_base}/cases_g${group}_c${case_id}"
    local rag_args=()
    if [ -n "$RAG" ]; then
        rag_args=(--rag "$RAG" --curated_pipeline_db "$RAG_DB" --curated_pipeline_norm_stats "$RAG_STATS")
    fi
    local drop_args=()
    if [ -n "$DROP_SCORE_COMPONENTS" ]; then
        drop_args=(--drop_score_components "$DROP_SCORE_COMPONENTS")
    fi

    log "$tag" "Starting case ${group}_${case_id}"
    python3 Langraph/mcts_search.py \
        --benchmark          smart_building_v2 \
        --model              "$model" \
        --token_limit        12000 \
        --source_length      3 \
        --target_length      3 \
        --mcts_iterations    40 \
        --early_stopping     0 \
        --same_leaf_stopping "$SAME_LEAF_STOPPING" \
        --case_timeout       "$CASE_TIMEOUT" \
        --mcts_critique_mode simulate \
        --validation         autopipeline \
        --reward             det_score_value \
        --simulation         pipeline \
        --data_split         training \
        "${rag_args[@]}" \
        "${drop_args[@]}" \
        --length          "$group" \
        --id_start        "$case_id" \
        --id_end          "$case_id" \
        --experiment_name "$exp_name" \
        --log_dir         "$case_log_dir" \
        --result_dir      "$result_dir" \
        &> "$stdout_log" || log "$tag" "WARNING: see $stdout_log"

    if grep -qE "credit_balance_exhausted|no credits remaining|insufficient_quota" "$stdout_log" 2>/dev/null; then
        log "$tag" "*** API CREDITS EXHAUSTED -- results from here are INVALID. Abort and top up. ***"
    fi
    log "$tag" "Done"
}

enqueue() {
    while [ "$(jobs -rp | wc -l)" -ge "$MAX_JOBS" ]; do wait -n 2>/dev/null || sleep 1; done
    run_case "$@" &
}

t0=$(date +%s)
for MODEL in $MODELS; do
    check_disk || { log "ABORT" "disk check failed before $MODEL -- stopping the whole run"; exit 1; }
    mkdir -p "logs_langraph/smartbuilding_v2_${RUN_TAG}_${MODEL}"
    log "ALL" "===== $MODEL: ${#CASES[@]} cases, MAX_JOBS=${MAX_JOBS}, case_timeout=${CASE_TIMEOUT}s, same_leaf_stopping=${SAME_LEAF_STOPPING}, drop_score_components=${DROP_SCORE_COMPONENTS:-none} ====="
    m_start=$(date +%s)
    for u in "${CASES[@]}"; do enqueue "$MODEL" "${u%%:*}" "${u##*:}"; done
    wait
    log "ALL" "$MODEL complete in $(( ($(date +%s)-m_start)/60 )) min   free disk: $(df -h / | awk 'NR==2{print $4}')"
done
log "ALL" "ALL MODELS COMPLETE in $(( ($(date +%s)-t0)/60 )) min"

echo
echo "================ RESULTS ================"
python3 - "$RUN_TAG" "$MODELS" <<'PY'
import sys, csv, glob
run_tag, models = sys.argv[1], sys.argv[2].split()
for model in models:
    rows = []
    for f in sorted(glob.glob(f"Langraph/results_langraph/smartbuilding_v2_{run_tag}_{model}/*/results_summary.csv")):
        with open(f) as fh:
            rows.extend(csv.DictReader(fh))
    correct = sum(1 for r in rows if r.get("is_correct", "").strip().lower() in ("true", "1"))
    total = len(rows)
    print(f"\n  {model}: {correct}/{total} correct (of {total} run)")
    for r in sorted(rows, key=lambda r: tuple(int(x) for x in (r.get("case_id") or r.get("id")).split("_"))):
        cid = r.get("case_id") or r.get("id")
        ic = r.get("is_correct", "").strip().lower() in ("true", "1")
        print(f"    {cid:6} {'PASS' if ic else 'FAIL'}  score={r.get('best_score')}  status={r.get('status')}")
    if total < 20:
        print(f"  WARNING: only {total} cases produced a results_summary.csv.")
PY
