#!/bin/bash
# TreeMorpher (Langraph/mcts_search.py) on the GitHub-pipelines benchmark, for Microsoft DMX
# models, with early leaf stopping ON (same_leaf_stopping=5) and curated-pipeline RAG ON.
# One phase only: a single attempt per case, no retry pass.
#
# Arguments follow the existing gpt-4.1-mini curated-RAG runs (run_curated_pipeline_l1_l2_l4_l6_l9.sh,
# run_rag_det_score_run38/40/43_*.sh): det_score_value reward, pipeline simulation, simulate critique,
# 40 iterations, autopipeline validation, --data_split training (scored on training data, then
# validated on held-out test data), --rag curated_pipeline, and --max_depth passed explicitly per length
# (L1=2 L2=2 L3=3 L4=4 L5=5 L6=2 L9=2 = MAX_DEPTH_BY_LENGTH in mcts_search.py). Only the model differs
# (dmx-*), plus --case_timeout 600 (those runs used the 300s default with a faster model).
#
# MEMORY / DISK WARNING (from run_rag_det_score_run43's header): L4 at 20 jobs exhausted 62 GB of RAM,
# OOM-killing cases and orphaning multi-GB join_rank_scratch_*.csv files that filled the disk to 99%.
# Each finished case's scratch files are removed below, but that does not prevent OOM. Watch
# `free -g` and `df -h /` when L4/L5 start; if tight, stop and resume the same RUN_TAG with a lower
# MAX_JOBS (finished cases are skipped), e.g.  RUN_TAG=<tag> LENGTHS=4 MAX_JOBS=8 bash run_github_mcts_dmx.sh
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_github_mcts_dmx.sh
#
# GitHub has lengths 1,2,3,4,5,6,9 (no 7 or 8 folders); ids are 0-based with gaps, so cases are
# discovered from the folders on disk: 698 cases in total.
#
# Needs (NOT in git, copy them if missing): rag_pipeline/db/curated_pipeline_656.db and
# rag_pipeline/db/curated_pipeline_features.norm_stats.json
#
# Overrides:
#     RAG=curated_pipeline       (default; RAG="" runs without RAG -- do not, unless comparing)
#     MODELS="dmx-gpt-oss-120b"                          (default: ONE model; several would run one after another)
#     LENGTHS="1 2 3 4 5 6 9"                            (default; ids without a folder are skipped)
#     MAX_JOBS=20                CASE_TIMEOUT=600     SAME_LEAF_STOPPING=5     MIN_FREE_GB=15
#     CASE_TIMEOUT_BY_LENGTH="2=480 3=480 6=480 9=480"   per-length case timeout in seconds (others use CASE_TIMEOUT)
#     RUN_TAG=<tag>              default gh_leafstop5_<launch timestamp>. Re-launch with the SAME
#                                RUN_TAG to RESUME: cases that already have a results_summary.csv
#                                in that run are skipped.
#     CASES_OVERRIDE="1_41 4_18" only these cases (L_id tokens)
#     DRY_RUN=1                  print the case list / counts and exit (no LLM calls)
#
# Models run one after another: MCTS writes python_recovered_mcts.py / target_multisource_mcts*.csv
# into the SAME benchmark case folders whichever model produced them, so two models on the same
# case at once would clobber each other. The script refuses to start if another MCTS run is active.
#
# Output (relative to Langraph/ for results, repo root for logs):
#     results_langraph/github_<RUN_TAG>_<model>/<case run dir>/results_summary.csv
#     logs_langraph/github_<RUN_TAG>_<model>/cases_g<L>_c<id>/*_MCTS_*.log   (tokens are in here)

cd "$(dirname "$0")" || exit 1

MODELS="${MODELS:-dmx-gpt-oss-120b}"
LENGTHS="${LENGTHS:-1 2 3 4 5 6 9}"
MAX_JOBS="${MAX_JOBS:-20}"
CASE_TIMEOUT="${CASE_TIMEOUT:-600}"
# Optional per-length timeouts, e.g. CASE_TIMEOUT_BY_LENGTH="2=480 3=480 6=480 9=480"; a length not listed uses CASE_TIMEOUT.
CASE_TIMEOUT_BY_LENGTH="${CASE_TIMEOUT_BY_LENGTH:-}"
timeout_for() {
    local kv
    for kv in $CASE_TIMEOUT_BY_LENGTH; do
        if [ "${kv%%=*}" = "$1" ]; then echo "${kv##*=}"; return; fi
    done
    echo "$CASE_TIMEOUT"
}
SAME_LEAF_STOPPING="${SAME_LEAF_STOPPING:-5}"
MIN_FREE_GB="${MIN_FREE_GB:-15}"
RUN_TAG="${RUN_TAG:-gh_leafstop5_$(date '+%Y%m%d_%H%M%S')}"
BENCH_DIR="autopipeline-benchmarks/github-pipelines"

log() { echo "[$(date '+%H:%M:%S')] [$1] $2"; }

# ---- build the case list ("L:id" tokens) --------------------------------------------------
CASES=()
if [ -n "${CASES_OVERRIDE:-}" ]; then
    for tok in $CASES_OVERRIDE; do CASES+=("${tok/_/:}"); done
else
    for L in $LENGTHS; do
        while IFS= read -r id; do CASES+=("${L}:${id}"); done < <(
            ls -d "${BENCH_DIR}/length${L}_"* 2>/dev/null | sed "s|.*/length${L}_||" | sort -n)
    done
fi

if [ -n "${DRY_RUN:-}" ]; then
    echo "RUN_TAG=$RUN_TAG  MODELS=$MODELS  MAX_JOBS=$MAX_JOBS  same_leaf_stopping=$SAME_LEAF_STOPPING  timeout=${CASE_TIMEOUT}s  rag=${RAG-curated_pipeline}"
    echo "total cases per model: ${#CASES[@]}"
    for L in $LENGTHS; do
        n=0; for u in "${CASES[@]}"; do [ "${u%%:*}" = "$L" ] && n=$((n+1)); done
        echo "  length $L: $n cases  (timeout $(timeout_for "$L")s)"
    done
    exit 0
fi

if ! python3 -c "import transformers" 2>/dev/null; then
    echo "ERROR: venv not active (transformers missing). run:  source env/bin/activate" >&2
    exit 1
fi

RAG="${RAG-curated_pipeline}"
RAG_DB="rag_pipeline/db/curated_pipeline_656.db"
RAG_STATS="rag_pipeline/db/curated_pipeline_features.norm_stats.json"
if [ "$RAG" = "curated_pipeline" ]; then
    for f in "$RAG_DB" "$RAG_STATS"; do
        [ -s "$f" ] || { echo "ERROR: RAG file missing: $f (see the header: it is not in git)" >&2; exit 1; }
    done
fi

# SKIP_GUARD=1 bypasses this check (e.g. when leftover child processes of a finished run still match).
if [ -z "${SKIP_GUARD:-}" ] && pgrep -u "$(id -u)" -f "Langraph/mcts_search\.py|python3 critique_data\.py" >/dev/null; then
    echo "ERROR: an MCTS or critique_data.py run is already active. Both write into the" >&2
    echo "  same benchmark case folders; wait for it to finish first." >&2
    exit 1
fi

check_disk() {
    local free_gb
    free_gb=$(df --output=avail -BG / | tail -1 | tr -dc '0-9')
    if [ "$free_gb" -lt "$MIN_FREE_GB" ]; then
        echo "ERROR: only ${free_gb}G free on / (need >= ${MIN_FREE_GB}G). Override with MIN_FREE_GB=<n>." >&2
        return 1
    fi
}
check_disk || exit 1

for m in $MODELS; do
    case "$m" in
        dmx-*)
            code=$(curl -s -m 10 -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/v1/chat/completions)
            if [ "$code" = "000" ]; then
                echo "ERROR: $m needs the SSH tunnel -- nothing is listening on localhost:8000." >&2
                echo "  run:  ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>" >&2
                exit 1
            fi ;;
    esac
done

# dmx-deepseek-* loads the DeepSeek-V3 tokenizer via AutoTokenizer.from_pretrained(), which hits
# huggingface.co unless offline; warm the cache once, then go offline (avoids 429s under concurrency).
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

run_case() {
    local model=$1 group=$2 case_id=$3
    local result_dir="results_langraph/github_${RUN_TAG}_${model}"
    local log_base="logs_langraph/github_${RUN_TAG}_${model}"
    local exp_name="github_${RUN_TAG}_${model}_g${group}_c${case_id}"
    local tag="${model}_G${group}_C${case_id}"
    local stdout_log="${log_base}/stdout_g${group}_c${case_id}.log"
    local case_log_dir="${log_base}/cases_g${group}_c${case_id}"
    local max_depth case_timeout
    case_timeout=$(timeout_for "$group")
    case "$group" in 1|2|6|9) max_depth=2 ;; 3) max_depth=3 ;; 4) max_depth=4 ;; 5) max_depth=5 ;; *) max_depth=2 ;; esac
    local rag_args=()
    if [ -n "$RAG" ]; then
        rag_args=(--rag "$RAG" --curated_pipeline_db "$RAG_DB" --curated_pipeline_norm_stats "$RAG_STATS")
    fi

    # Resume: result dirs are Langraph/results_langraph/<exp_name>_<timestamp>/ ("_2..." = year prefix,
    # so c1 never matches c10). A case counts as done only if its results_summary.csv has a DATA row:
    # a case killed mid-run leaves a header-only file (1 line), and must be run again.
    local f
    for f in Langraph/${result_dir}/${exp_name}_2*/results_summary.csv; do
        if [ -f "$f" ] && [ "$(wc -l < "$f")" -gt 1 ]; then
            log "$tag" "already done -- skipping"
            return
        fi
    done

    log "$tag" "Starting case ${group}_${case_id}"
    python3 Langraph/mcts_search.py \
        --benchmark          github \
        --model              "$model" \
        --token_limit        12000 \
        --source_length      3 \
        --target_length      3 \
        --mcts_iterations    40 \
        --early_stopping     0 \
        --same_leaf_stopping "$SAME_LEAF_STOPPING" \
        --case_timeout       "$case_timeout" \
        --mcts_critique_mode simulate \
        --validation         autopipeline \
        --reward             det_score_value \
        --simulation         pipeline \
        --data_split         training \
        "${rag_args[@]}" \
        --max_depth          "$max_depth" \
        --length             "$group" \
        --id_start           "$case_id" \
        --id_end             "$case_id" \
        --experiment_name    "$exp_name" \
        --log_dir            "$case_log_dir" \
        --result_dir         "$result_dir" \
        &> "$stdout_log" || log "$tag" "WARNING: see $stdout_log"

    # Scratch cleanup (see the header): a SIGKILLed case can't remove its own join_rank_scratch_*.csv,
    # and on L4 they are multi-GB each. Sweep this case's files however it finished.
    rm -f "${BENCH_DIR}/length${group}_${case_id}"/join_rank_scratch_*.csv 2>/dev/null

    if grep -qE "credit_balance_exhausted|no credits remaining|insufficient_quota" "$stdout_log" 2>/dev/null; then
        log "$tag" "*** API CREDITS EXHAUSTED -- results from here are INVALID. Abort and top up. ***"
    fi
    log "$tag" "Done"
}

enqueue() {
    while [ "$(jobs -rp | wc -l)" -ge "$MAX_JOBS" ]; do wait -n 2>/dev/null || sleep 1; done
    run_case "$@" &
}

print_summary() {
    python3 - "$RUN_TAG" "$1" "${#CASES[@]}" <<'PY'
import sys, csv, glob, collections
tag, model, expected = sys.argv[1], sys.argv[2], int(sys.argv[3])
best = {}
for f in sorted(glob.glob(f"Langraph/results_langraph/github_{tag}_{model}/*/results_summary.csv")):
    for r in csv.DictReader(open(f)):
        best[r.get("case_id") or r.get("id")] = r
by = collections.defaultdict(lambda: [0, 0])
for cid, r in best.items():
    L = cid.split("_")[0]
    by[L][1] += 1
    by[L][0] += r.get("is_correct", "").strip().lower() in ("true", "1")
ok = sum(v[0] for v in by.values())
print(f"\n  {model}: {ok}/{expected} correct ({100.0 * ok / expected:.1f}%), {len(best)} of {expected} cases produced a result")
print("    " + "  ".join(f"L{L}: {v[0]}/{v[1]}" for L, v in sorted(by.items(), key=lambda kv: int(kv[0]))))
if len(best) < expected:
    print(f"    WARNING: {expected - len(best)} case(s) have no results_summary.csv (crash/never ran) -- rerun with RUN_TAG={tag} to resume")
PY
}

t0=$(date +%s)
log "ALL" "RUN_TAG=${RUN_TAG}  (re-launch with this RUN_TAG to resume)"
for MODEL in $MODELS; do
    check_disk || { log "ABORT" "disk check failed before $MODEL -- stopping the whole run"; exit 1; }
    mkdir -p "logs_langraph/github_${RUN_TAG}_${MODEL}"
    log "ALL" "===== $MODEL: ${#CASES[@]} cases, MAX_JOBS=${MAX_JOBS}, case_timeout=${CASE_TIMEOUT}s, same_leaf_stopping=${SAME_LEAF_STOPPING}, rag=${RAG:-none} ====="
    m_start=$(date +%s)
    for u in "${CASES[@]}"; do enqueue "$MODEL" "${u%%:*}" "${u##*:}"; done
    wait
    log "ALL" "$MODEL complete in $(( ($(date +%s)-m_start)/60 )) min   free disk: $(df -h / | awk 'NR==2{print $4}')"
done
log "ALL" "ALL MODELS COMPLETE in $(( ($(date +%s)-t0)/60 )) min"

echo
echo "================ RESULTS (RUN_TAG=${RUN_TAG}) ================"
for MODEL in $MODELS; do print_summary "$MODEL"; done
