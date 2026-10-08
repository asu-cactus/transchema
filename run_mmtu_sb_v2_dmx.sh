#!/bin/bash
# MMTU baseline (Transform-by-output-target-schema, one-shot prompt) on smart_building_v2,
# all 105 cases, for a Microsoft DMX model -- the same run as the earlier gpt-4.1-mini one
# (MMTU/results_smartbuilding_v2), pointed at the DMX proxy instead of OpenAI.
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_mmtu_sb_v2_dmx.sh
#
# Overrides:
#     MODEL="dmx-gpt-oss-120b"   (default; any dmx-* model works, e.g. dmx-deepseek-v4-pro)
#     N_PARALLEL=20              concurrent LLM requests through the proxy
#     RUN_SUFFIX=""              set e.g. _p10 to keep a rerun's results separate from the default run's
#     LENGTH=""                  set to e.g. 1 to run/score only one length bucket
#     EVAL_ONLY=1                skip the LLM queries and only (re)score existing responses
#
# Resumable: run_openai_task.py skips rows that already have a non-empty response in the
# result file, so rerunning after a crash or a batch of failed requests only queries the
# missing/empty ones.
#
# Output (relative to MMTU/):
#     results_smartbuilding_v2_dmx/mmtu.<model>.result.jsonl   raw model responses
#     eval_sb_v2_dmx_<model>/<model>_details.csv               per-case is_correct + reason
#     eval_sb_v2_dmx_<model>/<model>_summary.csv

cd "$(dirname "$0")" || exit 1
R=$PWD

MODEL="${MODEL:-dmx-gpt-oss-120b}"
N_PARALLEL="${N_PARALLEL:-20}"
QUERY_DELAY="${QUERY_DELAY:-0}"      # seconds each worker waits after a query (staggers requests; 5 avoids the proxy's 429s at 10 workers)
RATE_CALLS="${RATE_CALLS:-0}"           # e.g. 5 with RATE_PERIOD=30: at most 5 request starts per 30 s across ALL workers (0 = off)
RATE_PERIOD="${RATE_PERIOD:-30}"
RETRY_ATTEMPTS="${RETRY_ATTEMPTS:-6}"   # patient mode for a shared, rate-limited deployment: e.g. 20
RETRY_MAX_WAIT="${RETRY_MAX_WAIT:-30}"  # e.g. 60
RUN_SUFFIX="${RUN_SUFFIX:-}"      # e.g. _p10: writes to results_smartbuilding_v2_dmx_p10/ and eval_sb_v2_dmx_p10_<model>/ so a rerun never resumes from (or overwrites) an earlier run
LENGTH="${LENGTH:-}"
EVAL_ONLY="${EVAL_ONLY:-}"
TAG="${MODEL//./-}"; TAG="${TAG//:/-}"      # same sanitising run_openai_task.py applies

if ! python3 -c "import transformers" 2>/dev/null; then
    echo "ERROR: venv not active (transformers missing). run:  source env/bin/activate" >&2
    exit 1
fi

# Sandboxes are written per eval run and never cleaned up by the evaluator; refuse to start
# on a nearly-full disk (a full disk silently truncated an earlier results file to 0 bytes).
free_gb=$(df --output=avail -BG / | tail -1 | tr -dc '0-9')
if [ "$free_gb" -lt 10 ]; then
    echo "ERROR: only ${free_gb}G free on / (need >= 10G)." >&2
    exit 1
fi

if [ -z "$EVAL_ONLY" ]; then
    if [[ "$MODEL" == dmx-* ]]; then
        code=$(curl -s -m 10 -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/v1/chat/completions)
        if [ "$code" = "000" ]; then
            echo "ERROR: nothing is listening on localhost:8000 -- start the SSH tunnel:" >&2
            echo "  ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>" >&2
            exit 1
        fi
    elif [ -z "${OPENAI_API_KEY:-}" ]; then
        echo "ERROR: MODEL=$MODEL is not a dmx-* model and \$OPENAI_API_KEY is not set." >&2
        exit 1
    fi

    # HF_HUB_OFFLINE: llm_models.py loads a HuggingFace tokenizer at import time for some
    # models; offline mode avoids the 429s seen under concurrency. Harmless for gpt-oss.
    HF_HUB_OFFLINE=1 python3 MMTU/run_openai_task.py \
        --task        Transform-by-output-target-schema \
        --dataset     smart_building_v2 \
        --mmtu_jsonl  MMTU/mmtu_smartbuilding_v2.jsonl \
        --output_dir  "MMTU/results_smartbuilding_v2_dmx${RUN_SUFFIX}" \
        --model       "$MODEL" \
        --n_parallel  "$N_PARALLEL" \
        --delay_seconds "$QUERY_DELAY" \
        --rate_limit_calls "$RATE_CALLS" --rate_limit_period "$RATE_PERIOD" \
        --retry_attempts "$RETRY_ATTEMPTS" --retry_max_wait "$RETRY_MAX_WAIT" \
        ${LENGTH:+--length "$LENGTH"} \
        || { echo "run_openai_task.py failed" >&2; exit 1; }
fi

RESULT="$R/MMTU/results_smartbuilding_v2_dmx${RUN_SUFFIX}/mmtu.${TAG}.result.jsonl"
[ -s "$RESULT" ] || { echo "ERROR: $RESULT missing or empty" >&2; exit 1; }
n_empty=$(python3 - "$RESULT" <<'PY'
import sys, json
print(sum(1 for l in open(sys.argv[1]) if l.strip() and not json.loads(l).get("response")))
PY
)
echo "responses with EMPTY content (failed requests): $n_empty  (rerun this script to retry them)"

# Paths MUST be absolute: evaluate_autopipeline.py resolves case_dir after os.chdir(sandbox).
before=$(ls -d "$R"/MMTU/tmp_exec/autopipeline_eval_* 2>/dev/null | sort)
python3 MMTU/evaluate_autopipeline.py "$RESULT" \
    --data_root "$R/autopipeline-benchmarks/smartbuilding-pipelines-v2-split" \
    ${LENGTH:+--length "$LENGTH"} --workers 4 --timeout 60 \
    --output_dir "$R/MMTU/eval_sb_v2_dmx${RUN_SUFFIX}_${TAG}" 2>&1 | grep -vE "Evaluating:|it/s"

# Remove only the sandbox this evaluation created.
after=$(ls -d "$R"/MMTU/tmp_exec/autopipeline_eval_* 2>/dev/null | sort)
comm -13 <(echo "$before") <(echo "$after") | xargs -r rm -rf

python3 - "$R/MMTU/eval_sb_v2_dmx${RUN_SUFFIX}_${TAG}/${TAG}_details.csv" "$MODEL" <<'PY'
import sys, pandas as pd
try:
    d = pd.read_csv(sys.argv[1])
except FileNotFoundError:
    raise SystemExit(f"no details CSV at {sys.argv[1]} -- check disk space (df -h /)")
print(f"\nMMTU {sys.argv[2]}, smart_building_v2: {int(d.is_correct.sum())}/{len(d)} = {d.is_correct.mean():.1%}")
for L in sorted(d.length.unique()):
    x = d[d.length == L]
    print(f"  L{L:<3} {int(x.is_correct.sum())}/{len(x)}")
print("\nreasons:", d.reason.value_counts().to_dict())
PY
