#!/bin/bash
# Same three-arm model comparison as run_sb20_arms_timing.sh / run_sb85_rest_timing.sh,
# but for the deepseek DMX models and all 105 smart_building_v2 cases in one script
# (no separate pilot/rest split -- LENGTHS covers L1-L15 in a single pass per arm):
#
#   coocrit   CoO + Critique   run_sb_rest_cot_coo.sh ARMS=coo   (1 critique round; also gives CoO)
#   cooreact  CoO + ReAct      run_sb_react_coo.sh               (materialization, 1 critique round)
#   cotreact  CoT + ReAct      run_sb_react_cot.sh               (40 rounds, no ES; also gives CoT
#                                                                  and CoT+Critique via round 0/1)
#
# TAGS MATCH run_sb20_arms_timing.sh / run_sb85_rest_timing.sh exactly
# (sb20_<arm>_timing_<model>_l<L>), so analyze_sb105_arms_dmx_oss.py works unchanged:
#   python3 analyze_sb105_arms_dmx_oss.py dmx-deepseek-v4-flash
#   python3 analyze_sb105_arms_dmx_oss.py dmx-deepseek-v4-pro
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>       # other terminal
#     bash alternate_baselines/run_sb105_arms_timing.sh
#
# Overrides: MODELS="dmx-deepseek-v4-pro" / ARMS="cotreact" to run a subset.
# Re-running resumes: the runners skip any case that already has a JSON (SKIP_DONE=1).
#
# MODELS RUN ONE AFTER ANOTHER, and so do the three arms within a model: every phase
# writes into the same benchmark case folders and critique_data.py wipes
# python_recovered.py / target_multisource* there at case start, so two phases on the
# same case at the same time would delete each other's output. Within one phase all 105
# cases queue through MAX_JOBS=20 concurrent slots.
#
# DISK: the 2026-09-16 gpt-oss-120b run filled the root disk mid-run (CoT+ReAct writes a
# target_multisource_critique_roundN.csv per round, up to 40/case) and several L9-L15
# cases came out with unreliable results (see analyze_sb105_arms_dmx_oss.py's "disk-full
# errors" section). This script refuses to start below MIN_FREE_GB and re-checks before
# each phase, so a slow leak stops the run instead of silently corrupting results.
#
# Expected time per model: CoO+Critique and CoO+ReAct ~30-45 min each; CoT+ReAct cases
# run up to the 600s cap, so ~60-90 min. Roughly 2-3 hours per model, 4-6 hours for both.

cd "$(dirname "$0")/.." || exit 1

if ! python3 -c "import transformers" 2>/dev/null; then
    echo "ERROR: venv not active (transformers missing)." >&2
    echo "  run:  source env/bin/activate" >&2
    exit 1
fi

if pgrep -u "$(id -u)" -f "python3 critique_data.py" >/dev/null; then
    echo "ERROR: critique_data.py is already running. Every phase here writes into the" >&2
    echo "  same case folders as any other run; wait for it to finish first." >&2
    exit 1
fi

MODELS="${MODELS:-dmx-deepseek-v4-flash dmx-deepseek-v4-pro}"
ARMS="${ARMS:-coocrit cooreact cotreact}"
ROUNDS="${ROUNDS:-40}"            # CoT+ReAct round cap; CoO+ReAct is fixed at 1 round
MAX_JOBS="${MAX_JOBS:-20}"        # was hardcoded 20 in every phase call below; now overridable
LENGTHS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"
MIN_FREE_GB="${MIN_FREE_GB:-15}"
LOG_ROOT="logs-auto-suggest-llm-21-04"
TIMING_FILE="${LOG_ROOT}/sb105_arms_timing_phases.tsv"

log() { echo "[$(date '+%H:%M:%S')] [ARMS105] $*"; }

# dmx_encoding() (llm_models.py) loads the DeepSeek-V3 tokenizer via
# AutoTokenizer.from_pretrained() -- and critique.py rebuilds a fresh LLMClient (so a
# fresh tokenizer load) on EVERY critique round, not once per case. That call hits
# huggingface.co over the network to check for updates unless told not to, and the
# 2026-09-16 run had up to 40 rounds x 20 concurrent cases all doing this at once, which
# got hard-rate-limited (HTTP 429) partway through -- ~85% of cases crashed on a
# tokenizer load, most before making any LLM request at all (see the postmortem in this
# session). Fix: HF_HUB_OFFLINE=1 skips that network check and reads the local cache
# only -- verified with 60 concurrent loads, 0 failures, well above real-run concurrency.
# The preflight load below is WITHOUT offline mode, so a genuinely cold/cleared cache
# fails once here with one clear error instead of silently killing every case.
if [[ " $MODELS " == *" dmx-deepseek"* ]]; then
    if ! python3 -c "
import os
os.environ.pop('HF_HUB_OFFLINE', None)
from transformers import AutoTokenizer
AutoTokenizer.from_pretrained('deepseek-ai/DeepSeek-V3')
" 2>/tmp/dmx_tokenizer_preflight.log; then
        echo "ERROR: could not load/download the DeepSeek-V3 tokenizer (needed for every" >&2
        echo "  dmx-deepseek-* case). See /tmp/dmx_tokenizer_preflight.log" >&2
        exit 1
    fi
    export HF_HUB_OFFLINE=1
    log "tokenizer cache warm -- HF_HUB_OFFLINE=1 set for the rest of this run"
fi

check_disk() {
    local free_gb
    free_gb=$(df --output=avail -BG / | tail -1 | tr -dc '0-9')
    if [ "$free_gb" -lt "$MIN_FREE_GB" ]; then
        echo "ERROR: only ${free_gb}G free on / (need >= ${MIN_FREE_GB}G). A prior run filled" >&2
        echo "  the disk mid-experiment and produced unreliable results -- free space first" >&2
        echo "  (round CSVs under autopipeline-benchmarks/*/length*_*/ are the usual bloat)." >&2
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
        *gpt-oss*)
            if [ -z "${OPENSOURCE_API_KEY:-}" ]; then
                echo "ERROR: $m needs \$OPENSOURCE_API_KEY. Run:" >&2
                echo '  eval "$(grep -E '"'"'^export OPENSOURCE_API_KEY='"'"' ~/.bashrc)"' >&2
                exit 1
            fi ;;
    esac
done
for a in $ARMS; do
    case "$a" in coocrit|cooreact|cotreact) ;; *) echo "ERROR: unknown arm '$a'" >&2; exit 1 ;; esac
done

[ -f "$TIMING_FILE" ] || printf "model\tarm\ttag\tstart_epoch\tend_epoch\twall_seconds\n" > "$TIMING_FILE"
log "models: $MODELS | arms: $ARMS | lengths: $LENGTHS (105 cases) | CoT+ReAct rounds<=$ROUNDS | min free ${MIN_FREE_GB}G"
t0=$(date +%s)

for MODEL in $MODELS; do
    for ARM in $ARMS; do
        check_disk || { log "ABORT" "disk check failed before $MODEL/$ARM -- stopping the whole run"; exit 1; }
        tag="sb20_${ARM}_timing_${MODEL}"
        log "===== $MODEL / $ARM -> ${LOG_ROOT}/${tag}_l{1..15} ====="
        start=$(date +%s)
        case "$ARM" in
            coocrit)
                LENGTHS="$LENGTHS" MODEL="$MODEL" TAG="$tag" MAX_JOBS="$MAX_JOBS" ARMS="coo" TOKEN_LIMIT=12000 \
                    bash alternate_baselines/run_sb_rest_cot_coo.sh
                sub=coo ;;
            cooreact)
                LENGTHS="$LENGTHS" MODEL="$MODEL" TAG="$tag" MAX_JOBS="$MAX_JOBS" ROUNDS=1 NO_ES=0 \
                    bash alternate_baselines/run_sb_react_coo.sh
                sub=coo ;;
            cotreact)
                LENGTHS="$LENGTHS" MODEL="$MODEL" TAG="$tag" MAX_JOBS="$MAX_JOBS" ROUNDS="$ROUNDS" \
                    bash alternate_baselines/run_sb_react_cot.sh
                sub=cot ;;
        esac
        end=$(date +%s)
        printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$MODEL" "$ARM" "$tag" "$start" "$end" "$((end - start))" >> "$TIMING_FILE"
        done_n=0
        for L in $LENGTHS; do
            done_n=$(( done_n + $(ls ${LOG_ROOT}/${tag}_l${L}/${sub}/cases_c*/*/jsons/*.json 2>/dev/null | wc -l) ))
        done
        log "$MODEL / $ARM finished in $(( (end - start) / 60 )) min -- $done_n/105 cases produced a JSON"
    done
    log "$MODEL complete -- analyze with: python3 analyze_sb105_arms_dmx_oss.py $MODEL"
done

log "ALL DONE in $(( ($(date +%s) - t0) / 60 )) min -- phase timings in $TIMING_FILE"
