#!/usr/bin/env bash
# Runs the full smart_building v2 benchmark (105 cases, groups 1-15) through
# run_cases_iteratively.py with 20-way parallelism.
#
# Unlike v1 (a single fixed length_type=1), v2 spans 15 different length_types
# (groups), and run_cases_iteratively.py/main.py process exactly one
# length_type per invocation -- there's no way to pass a mixed-group case list
# in one call. So each worker here loops over its assigned (group, position)
# pairs and invokes run_cases_iteratively.py once per pair (--length_type G
# --cases P), all writing into the SAME result_dir (safe: each pair gets its own
# length{G}/length{G}_{P}.json). Each pair also gets its OWN predict dir
# (PREDICT_DIR/g{G}_c{P}): the evaluator writes a generically-named case_by_case_summary.csv
# that run_cases_iteratively.py then renames, so with a shared predict dir concurrent workers
# grabbed each other's file and ~18% of cases lost their score (dmx-gpt-oss-120b run).
#
# Overrides: TARGET_EXAMPLES=0 (target example rows added to the prompts)  N_WORKERS=20  CASE_TIMEOUT=600
#            BASE_PATH=<split dir>  MANIFEST=<csv>  VENV=<venv dir>  CASES_OVERRIDE="3_6 6_10"
# Usage:  bash run_smartbuilding_v2_parallel.sh [MODEL]      (default gpt-4.1-mini)
#   e.g.  bash run_smartbuilding_v2_parallel.sh dmx-gpt-oss-120b
# MODEL must be a key in src/llm/config.py's MODELS. dmx-* models go through the SSH
# tunnel to the Azure VM proxy (localhost:8000):
#   ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>
set -euo pipefail

cd "$(dirname "$0")"
source "${VENV:-/home/asurite.ad.asu.edu/jrtandel/transchema/env}/bin/activate"

BASE_PATH="${BASE_PATH:-/home/asurite.ad.asu.edu/jrtandel/transchema/autopipeline-benchmarks/smartbuilding-pipelines-v2-split}"
MANIFEST="${MANIFEST:-$BASE_PATH/split_manifest.csv}"
MODEL="${1:-gpt-4.1-mini}"
VALIDATION="autopipeline"
N_WORKERS="${N_WORKERS:-20}"
CASE_TIMEOUT="${CASE_TIMEOUT:-600}"   # hard per-case wall-clock cap (s); a killed case just goes unscored
RUN_TAG="$(date +%Y%m%d_%H%M%S)"

if [[ "$MODEL" == dmx-* ]]; then
    code=$(curl -s -m 10 -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/v1/chat/completions || true)
    if [ "$code" = "000" ] || [ -z "$code" ]; then
        echo "ERROR: $MODEL needs the SSH tunnel -- nothing is listening on localhost:8000." >&2
        echo "  run:  ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>" >&2
        exit 1
    fi
fi
RESULT_DIR="result/smart_building_v2/${MODEL}/execution_${RUN_TAG}"
# Per-case MCTS progress logs go in a per-run dir so runs of different models don't overwrite each other's.
export BAT_LLM_LOG_DIR="logs/smartbuilding_v2_llm_${MODEL//[.:]/-}_${RUN_TAG}"
export BAT_MCTS_LOG_DIR="logs/smartbuilding_v2_mcts_${MODEL//[.:]/-}_${RUN_TAG}"
PREDICT_DIR="predict/smart_building_v2/${MODEL}/execution_${RUN_TAG}"

# Flat list of "group:position" pairs, one per case, from the manifest.
mapfile -t PAIRS < <(tail -n +2 "$MANIFEST" | awk -F',' '{print $2":"$3}')
# CASES_OVERRIDE="3_6 6_10" runs only those cases ("L_id" tokens), same convention as the GitHub launchers.
if [ -n "${CASES_OVERRIDE:-}" ]; then
    PAIRS=()
    for tok in $CASES_OVERRIDE; do PAIRS+=("${tok/_/:}"); done
fi
echo "Total cases: ${#PAIRS[@]}"
echo "Result dir: $RESULT_DIR"
echo "Predict dir: $PREDICT_DIR"

CASE_LOGS="logs/smartbuilding_v2_parallel_${RUN_TAG}"
mkdir -p "$CASE_LOGS"
# Shared work queue: xargs -P keeps N_WORKERS cases running and gives the next case to whichever
# worker frees up first. One log file per case.
run_one_case() {
    pair="$1"
    group="${pair%%:*}"
    position="${pair##*:}"
    timeout "${CASE_TIMEOUT}s" python3 run_cases_iteratively.py \
        --length_type "$group" \
        --cases "$position" \
        --base_path "$BASE_PATH" \
        --result_dir "$RESULT_DIR" \
        --predict_dir "$PREDICT_DIR/g${group}_c${position}" \
        --validation "$VALIDATION" \
        --model_name "$MODEL" \
        --target_examples "${TARGET_EXAMPLES:-0}" \
        > "${CASE_LOGS}/g${group}_c${position}.log" 2>&1 \
        || echo "[$(date '+%H:%M:%S')] case ${group}_${position}: TIMED OUT or FAILED (see ${CASE_LOGS}/g${group}_c${position}.log)"
}
export -f run_one_case
export BASE_PATH RESULT_DIR PREDICT_DIR MODEL VALIDATION CASE_LOGS CASE_TIMEOUT TARGET_EXAMPLES

echo "Running ${#PAIRS[@]} cases through a shared queue, $N_WORKERS at a time..."
fail=0
printf '%s\n' "${PAIRS[@]}" | xargs -P "$N_WORKERS" -I{} bash -c 'run_one_case "$@"' _ {} || fail=1

echo "All cases finished (fail=$fail)."
echo "RESULT_DIR=$RESULT_DIR"
echo "PREDICT_DIR=$PREDICT_DIR"

python3 - "$PREDICT_DIR" "$MODEL" <<'PY'
import os, sys, glob, pandas as pd
pdir, model = sys.argv[1], sys.argv[2]
fs = glob.glob(f"{pdir}/*/master_results_*.csv") + glob.glob(f"{pdir}/master_results_*.csv")
if not fs:
    raise SystemExit(f"no master_results_*.csv under {pdir} -- check logs/smartbuilding_v2_parallel_*/*.log")
d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
d["correct"] = d.accuracy == 1.0
print(f"\nBAT {model}, smart_building_v2: {int(d.correct.sum())}/{len(d)} = {d.correct.mean():.1%}")
print(d.groupby("length_type").correct.agg(["sum", "count"]).T.to_string())
if len(d) != 105 and not os.environ.get("CASES_OVERRIDE"):
    missing = 105 - len(d)
    print(f"WARNING: {missing} of 105 cases have no result (worker crash / LLM failure) -- see the worker logs.")
PY
