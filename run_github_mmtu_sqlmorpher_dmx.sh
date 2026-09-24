#!/bin/bash
# MMTU + SQLMorpher on the GitHub-pipelines benchmark (698 cases) for DMX models: for each model,
# MMTU first, then SQLMorpher, strictly one after another. Default: ONE model, dmx-gpt-oss-120b.
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_github_mmtu_sqlmorpher_dmx.sh
#
# Overrides:
#     MODELS="dmx-gpt-oss-120b"       (default; several would run one after another)
#     N_WORKERS=15                    SQLMorpher parallel workers (also used as MMTU's N_PARALLEL)
#     SKIP_GUARD=1                    skip the "another SQLMorpher run is active" check
#
# Steps are sequential because SQLMorpher's per-case Postgres tables have fixed names (two runs
# would drop each other's tables). A failed step is logged and the remaining steps still run.
#
# Each step's full output goes to logs_langraph/github_<step>_<model>_run.log; results land where
# the two underlying scripts put them:
#     MMTU/eval_github_dmx_<model>/<model>_details.csv
#     ChatGPTwithSQLscript/logs/github_698_<model>_<ts>_merged_results.csv

cd "$(dirname "$0")" || exit 1
MODELS="${MODELS:-dmx-gpt-oss-120b}"
N_WORKERS="${N_WORKERS:-15}"

if ! python3 -c "import transformers" 2>/dev/null; then
    echo "ERROR: venv not active (transformers missing). run:  source env/bin/activate" >&2
    exit 1
fi

if [ -z "${SKIP_GUARD:-}" ] && pgrep -u "$(id -u)" -f "auto_pipeline_join\.py" >/dev/null; then
    echo "ERROR: a SQLMorpher run (auto_pipeline_join.py) is already active -- its Postgres tables" >&2
    echo "  would collide with this one. Wait for it, or set SKIP_GUARD=1." >&2
    exit 1
fi

if [[ " $MODELS " == *" dmx-"* ]]; then
    code=$(curl -s -m 10 -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/v1/chat/completions)
    if [ "$code" = "000" ]; then
        echo "ERROR: nothing is listening on localhost:8000 -- start the SSH tunnel:" >&2
        echo "  ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>" >&2
        exit 1
    fi
elif [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "ERROR: MODELS=$MODELS has no dmx-* model and \$OPENAI_API_KEY is not set." >&2
    exit 1
fi

mkdir -p logs_langraph
log() { echo "[$(date '+%H:%M:%S')] [GH MMTU+SQLM] $1"; }
SUMMARY=()

for MODEL in $MODELS; do
    for STEP in mmtu sqlmorpher; do
        out="logs_langraph/github_${STEP}_${MODEL}_run.log"
        log "===== $MODEL: $STEP (log: $out) ====="
        if [ "$STEP" = "mmtu" ]; then
            MODEL="$MODEL" N_PARALLEL="$N_WORKERS" bash run_mmtu_github_dmx.sh > "$out" 2>&1
        else
            N_WORKERS="$N_WORKERS" bash ChatGPTwithSQLscript/run_github_parallel.sh "$MODEL" > "$out" 2>&1
        fi
        rc=$?
        [ $rc -eq 0 ] || log "$MODEL $STEP exited with status $rc -- see $out"
        line=$(grep -E "^(MMTU|SQLMorpher) $MODEL" "$out" | tail -1)
        SUMMARY+=("${line:-$MODEL $STEP: NO SUMMARY LINE (status $rc) -- see $out}")
        log "${SUMMARY[-1]}"
    done
done

echo
echo "================ SUMMARY ================"
for line in "${SUMMARY[@]}"; do echo "  $line"; done
