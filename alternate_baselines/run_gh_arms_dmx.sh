#!/bin/bash
# CoO+Critique, CoO+ReAct and CoT+ReAct on the GitHub-pipelines benchmark (698 cases), for DMX models.
# Same three arms, settings and phase order as the smart-building run (run_sb105_arms_timing.sh and the
# run_sb_rest_cot_coo.sh / run_sb_react_coo.sh / run_sb_react_cot.sh runners it calls), pointed at GitHub:
#
#   coocrit   CoO + Critique   multi-step CoO generation + 1 mcts_style critique round (also gives plain CoO)
#   cooreact  CoO + ReAct      --intermediate_materialization, 1 critique round
#   cotreact  CoT + ReAct      --single_step_cot, up to ROUNDS=40 critique rounds, NO early stopping
#                              (round 0/1 of this run also give plain CoT and CoT+Critique)
#
# All arms: curated_pipeline RAG (top-3, 4000 tokens), mcts_style critique, autopipeline validation,
# --data_split training, token limit 12000, 600s per-case timeout (inside critique_data.py), NO rule hints
# (the smart-building runs left them off to isolate RAG; set RULE_HINTS=1 to add --rule-hints, as your
# gpt-4.1-mini GitHub ReAct runs used).
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>       # other terminal
#     bash alternate_baselines/run_gh_arms_dmx.sh
#
# GitHub has lengths 1,2,3,4,5,6,9 (no 7 or 8 folders); ids are 0-based with gaps, so cases are read from
# the folders on disk: 698 cases. One flat queue per phase, MAX_JOBS running at a time (a finished case
# immediately frees its slot). Arms run one after another: every arm writes the same files inside a case
# folder and critique_data.py wipes them at case start, so two arms on one case at once would delete each
# other's output.
#
# Overrides:
#     MODELS="dmx-gpt-oss-120b"        (default: ONE model)
#     ARMS="coocrit cooreact cotreact" (default; any subset)
#     LENGTHS="1 2 3 4 5 6 9"          MAX_JOBS=15    ROUNDS=40    MIN_FREE_GB=15    RULE_HINTS=1
#     SKIP_GUARD=1                     skip the "another MCTS/critique run is active" check
#     CASES_OVERRIDE="1_41 4_18"        only these cases (L_id tokens)
#     DRY_RUN=1                        print the case counts and settings, then exit (no LLM calls)
# Resumable: a case that already has a JSON for its arm is skipped (SKIP_DONE=1 by default). A JSON is
# flushed after every round, so a case killed part-way has one too -- delete that case's folder to redo it.
#
# Output:  logs-auto-suggest-llm-21-04/gh_<arm>_<model>_l<L>/<coo|cot>/cases_c<id>/*/jsons/*.json
# (logs-auto-suggest-llm-21-04 is a symlink to /media/harddisk; the per-round scratch CSVs are written into
# the benchmark case folders on the ROOT disk and are deleted as each case finishes.)

cd "$(dirname "$0")/.." || exit 1

MODELS="${MODELS:-dmx-gpt-oss-120b}"
ARMS="${ARMS:-coocrit cooreact cotreact}"
LENGTHS="${LENGTHS:-1 2 3 4 5 6 9}"
MAX_JOBS="${MAX_JOBS:-15}"
ROUNDS="${ROUNDS:-40}"
MIN_FREE_GB="${MIN_FREE_GB:-15}"
BENCH_DIR="${BENCH_DIR:-autopipeline-benchmarks/github-pipelines}"
LOG_ROOT="${LOG_ROOT:-logs-auto-suggest-llm-21-04}"
TIMING_FILE="${LOG_ROOT}/gh_arms_timing_phases.tsv"

log() { echo "[$(date '+%H:%M:%S')] [GH-ARMS] $*"; }

for a in $ARMS; do
    case "$a" in coocrit|cooreact|cotreact) ;; *) echo "ERROR: unknown arm '$a' (coocrit|cooreact|cotreact)" >&2; exit 1 ;; esac
done

# ---- case list ("L:id"), from the folders on disk ------------------------------------------------
CASES=()
for L in $LENGTHS; do
    while IFS= read -r id; do CASES+=("${L}:${id}"); done < <(
        ls -d "${BENCH_DIR}/length${L}_"* 2>/dev/null | sed "s|.*/length${L}_||" | sort -n)
done

# CASES_OVERRIDE="1_41 4_18" runs only those cases (L_id tokens), e.g. to redo a few.
if [ -n "${CASES_OVERRIDE:-}" ]; then
    CASES=()
    for tok in $CASES_OVERRIDE; do CASES+=("${tok/_/:}"); done
fi

if [ -n "${DRY_RUN:-}" ]; then
    echo "MODELS=$MODELS  ARMS=$ARMS  MAX_JOBS=$MAX_JOBS  ROUNDS=$ROUNDS  rule_hints=${RULE_HINTS:-off}  min_free=${MIN_FREE_GB}G"
    echo "cases per arm: ${#CASES[@]}"
    for L in $LENGTHS; do
        n=0; for u in "${CASES[@]}"; do [ "${u%%:*}" = "$L" ] && n=$((n+1)); done
        echo "  length $L: $n cases"
    done
    exit 0
fi

if ! python3 -c "import transformers" 2>/dev/null; then
    echo "ERROR: venv not active (transformers missing). run:  source env/bin/activate" >&2
    exit 1
fi

if [ -z "${SKIP_GUARD:-}" ] && pgrep -u "$(id -u)" -f "python3 critique_data\.py|Langraph/mcts_search\.py" >/dev/null; then
    echo "ERROR: a critique_data.py or MCTS run is already active. Every run writes into the same" >&2
    echo "  benchmark case folders; wait for it to finish (or SKIP_GUARD=1)." >&2
    exit 1
fi

check_disk() {
    local free_gb
    free_gb=$(df --output=avail -BG / | tail -1 | tr -dc '0-9')
    if [ "$free_gb" -lt "$MIN_FREE_GB" ]; then
        echo "ERROR: only ${free_gb}G free on / (need >= ${MIN_FREE_GB}G). CoT+ReAct writes a scratch CSV" >&2
        echo "  per round into the case folders; a full disk gives silently unreliable results." >&2
        echo "  Override with MIN_FREE_GB=<n> only if you have judged the risk." >&2
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

# dmx-deepseek-* loads the DeepSeek-V3 tokenizer on every critique round; go offline after one warm load
# (see run_sb105_arms_timing.sh for the 429 postmortem).
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
    log "tokenizer cache warm -- HF_HUB_OFFLINE=1 set for the rest of this run"
fi

COMMON_ARGS=(
    --benchmark          github
    --token-limit        12000
    --source-length      3
    --target-length      3
    --validation         autopipeline
    --data_split         training
    --critique_type      mcts_style
    --rag                curated_pipeline
    --curated_pipeline_db          rag_pipeline/db/curated_pipeline_656.db
    --curated_pipeline_norm_stats  rag_pipeline/db/curated_pipeline_features.norm_stats.json
    --rag_topk           3
    --rag_max_tokens     4000
)
[ -n "${RULE_HINTS:-}" ] && COMMON_ARGS+=(--rule-hints)

run_case() {
    local model=$1 arm=$2 sub=$3 L=$4 c=$5
    shift 5
    local tag="gh_${arm}_${model}"
    local base="${LOG_ROOT}/${tag}_l${L}"
    local case_log_dir="${base}/${sub}/cases_c${c}"
    if [ "${SKIP_DONE:-1}" = "1" ] && compgen -G "${case_log_dir}/*/jsons/*.json" >/dev/null 2>&1; then
        return 0
    fi
    mkdir -p "${base}/${sub}"
    log "${arm}_L${L}_C${c}" "start"
    python3 critique_data.py "${COMMON_ARGS[@]}" --model "$model" "$@" \
        --cases           "${L}_${c}" \
        --experiment-name "${tag}_l${L}_c${c}" \
        --log-dir         "$case_log_dir" \
        &> "${base}/stdout_${sub}_c${c}.log" || log "${arm}_L${L}_C${c}" "WARNING: see ${base}/stdout_${sub}_c${c}.log"
    log "${arm}_L${L}_C${c}" "done"
}

# Named scratch CSVs only (never a target_multisource*.csv wildcard: it would also delete an MCTS run's
# target_multisource_mcts*.csv). Every attempt's score is already in the case JSON.
cleanup_case() {
    local L="${1%%:*}" c="${1##*:}"
    rm -f "${BENCH_DIR}/length${L}_${c}"/target_multisource.csv \
          "${BENCH_DIR}/length${L}_${c}"/target_multisource_cot.csv \
          "${BENCH_DIR}/length${L}_${c}"/target_multisource_critique_history.csv \
          "${BENCH_DIR}/length${L}_${c}"/target_multisource_critique_history_test_val.csv \
          "${BENCH_DIR}/length${L}_${c}"/target_multisource_critique_round*.csv \
          "${BENCH_DIR}/length${L}_${c}"/target_multisource_test_val.csv \
          "${BENCH_DIR}/length${L}_${c}"/target_multisource_cot_test_val.csv \
          "${BENCH_DIR}/length${L}_${c}"/join_rank_scratch_*.csv 2>/dev/null
    rm -rf "${BENCH_DIR}/intermediate_space/length${L}_${c}" 2>/dev/null
}
declare -A JOB_CASE   # background job pid -> "L:c"
# Clean up a case only once ITS process has exited (a running case keeps rewriting these files).
reap_and_clean() {
    local pid
    for pid in "${!JOB_CASE[@]}"; do
        if ! kill -0 "$pid" 2>/dev/null; then
            cleanup_case "${JOB_CASE[$pid]}"
            unset 'JOB_CASE[$pid]'
        fi
    done
}
enqueue() {
    reap_and_clean
    while [ "$(jobs -rp | wc -l)" -ge "$MAX_JOBS" ]; do wait -n 2>/dev/null || sleep 1; done
    run_case "$@" &
    JOB_CASE[$!]="$4:$5"
}

[ -f "$TIMING_FILE" ] || printf "model\tarm\ttag\tstart_epoch\tend_epoch\twall_seconds\n" > "$TIMING_FILE"
log "models: $MODELS | arms: $ARMS | lengths: $LENGTHS (${#CASES[@]} cases) | ROUNDS<=$ROUNDS | MAX_JOBS=$MAX_JOBS | rule_hints=${RULE_HINTS:-off}"
t0=$(date +%s)

for MODEL in $MODELS; do
    for ARM in $ARMS; do
        check_disk || { log "ABORT" "disk check failed before $MODEL/$ARM -- stopping the whole run"; exit 1; }
        case "$ARM" in
            coocrit)  SUB=coo; ARM_ARGS=() ;;
            cooreact) SUB=coo; ARM_ARGS=(--critique-rounds 1 --intermediate_materialization) ;;
            cotreact) SUB=cot; ARM_ARGS=(--single_step_cot --critique-rounds "$ROUNDS" --no-early-stopping) ;;
        esac
        tag="gh_${ARM}_${MODEL}"
        log "===== $MODEL / $ARM -> ${LOG_ROOT}/${tag}_l{L}/${SUB} ====="
        start=$(date +%s)
        for u in "${CASES[@]}"; do enqueue "$MODEL" "$ARM" "$SUB" "${u%%:*}" "${u##*:}" "${ARM_ARGS[@]}"; done
        wait
        reap_and_clean
        end=$(date +%s)
        printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$MODEL" "$ARM" "$tag" "$start" "$end" "$((end - start))" >> "$TIMING_FILE"
        log "$MODEL / $ARM finished in $(( (end - start) / 60 )) min   free disk: $(df -h / | awk 'NR==2{print $4}')"
    done
done
log "ALL DONE in $(( ($(date +%s) - t0) / 60 )) min -- phase timings in $TIMING_FILE"

echo
echo "================ SUMMARY (correct / cases with a JSON) ================"
python3 - "$MODELS" "$ARMS" "$LENGTHS" "${#CASES[@]}" <<'PY'
import sys, glob, json
models, arms, lengths, total = sys.argv[1].split(), sys.argv[2].split(), sys.argv[3].split(), int(sys.argv[4])
sub = {"coocrit": "coo", "cooreact": "coo", "cotreact": "cot"}
for m in models:
    for a in arms:
        g = b1 = ball = n = 0
        per = []
        for L in lengths:
            ng = nb1 = nb = nn = 0
            for d in glob.glob(f"logs-auto-suggest-llm-21-04/gh_{a}_{m}_l{L}/{sub[a]}/cases_c*"):
                js = sorted(glob.glob(d + "/*/jsons/*.json"))
                if not js:
                    continue
                it = json.load(open(js[-1]))["iterations"][0]
                atts = [it["ms"]] + it.get("critiques", [])
                best = lambda xs: max(xs, key=lambda x: x.get("score") or 0.0)
                nn += 1; ng += bool(it["ms"]["is_correct"]); nb1 += bool(best(atts[:2])["is_correct"]); nb += bool(best(atts)["is_correct"])
            per.append(f"L{L}: {nb}/{nn}"); g += ng; b1 += nb1; ball += nb; n += nn
        print(f"{m} / {a}: {n}/{total} cases done | generation {g} | +round 1 {b1} | best of all rounds {ball}   ({'  '.join(per)})")
PY
