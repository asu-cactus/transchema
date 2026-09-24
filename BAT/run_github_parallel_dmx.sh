#!/usr/bin/env bash
# BAT on the GitHub-pipelines benchmark (698 cases: L1 100, L2 100, L3 100, L4 100, L5 98, L6 99, L9 101;
# ids are 0-based with gaps, so the case list is read from the folders on disk), for a DMX model.
# Same launcher as run_smartbuilding_v2_parallel.sh (which supersedes the older run_github_pipelines_parallel.sh:
# that one hard-codes gpt-4.1-mini, runs only 3 lengths at a time, and shares one predict dir):
#   * N_WORKERS background workers (default 20); each takes an equal round-robin share of the cases
#     and runs them one after another through run_cases_iteratively.py (one (length, case) per call),
#   * every case gets its OWN predict dir (PREDICT_DIR/g<L>_c<id>): the evaluator writes a generically named
#     case_by_case_summary.csv that is then renamed, so a shared predict dir made concurrent workers grab each
#     other's file and lose ~18% of the scores,
#   * per-run dirs for the per-case MCTS progress logs (BAT_MCTS_LOG_DIR) and the per-call LLM logs
#     (BAT_LLM_LOG_DIR): their file names carry no benchmark, and GitHub case ids (length1_1, ...) collide with
#     the smart-building ones, which would otherwise mix two benchmarks' tokens/latencies.
#
# Usage:  bash run_github_parallel_dmx.sh [MODEL]      (default dmx-gpt-oss-120b; a key in src/llm/config.py)
# dmx-* models go through the SSH tunnel to the Azure VM proxy (localhost:8000):
#   ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>
#
# Overrides:  N_WORKERS=20  LENGTHS="1 2 3 4 5 6 9"  DRY_RUN=1 (print the case counts and exit)
#             CASE_TIMEOUT=600  hard per-case wall-clock cap in seconds (see below)
#             SKIP_CASES="4_0 4_1 ... 4_18"  (space-separated "L_id" tokens) drop these cases from the run
#             CASES_OVERRIDE="4_0 9_17 ..."  (space-separated "L_id" tokens) run ONLY these cases
#                                             (takes priority over LENGTHS/SKIP_CASES)
# Output:     result/github-pipelines/<model>/execution_<TS>/   predict/github-pipelines/<model>/execution_<TS>/g<L>_c<id>/
#             logs/github_<model>_<TS>/{mcts,llm}/     (llm/llm_queries_<model>_length<L>.jsonl holds the tokens)
set -euo pipefail

cd "$(dirname "$0")"
MODEL="${1:-dmx-gpt-oss-120b}"
N_WORKERS="${N_WORKERS:-20}"
LENGTHS="${LENGTHS:-1 2 3 4 5 6 9}"
# Hard per-case wall-clock cap (seconds) -- BAT's own MCTS solver has NO timeout of its own,
# unlike every other tool in this project (TreeMorpher/critique_data.py all cap at 600s). A
# stuck case (observed: several ran 30-50+ min with no sign of finishing) blocks its worker
# forever. `timeout` SIGTERMs (then SIGKILLs) the case; `|| true` below keeps a killed/failed
# case from taking down the rest of that worker's queue under `set -e`.
CASE_TIMEOUT="${CASE_TIMEOUT:-600}"
BASE_PATH=/home/asurite.ad.asu.edu/jrtandel/transchema/autopipeline-benchmarks/github-pipelines
RUN_TAG="$(date +%Y%m%d_%H%M%S)"
RESULT_DIR="result/github-pipelines/${MODEL}/execution_${RUN_TAG}"
PREDICT_DIR="predict/github-pipelines/${MODEL}/execution_${RUN_TAG}"
RUN_LOGS="logs/github_${MODEL//[.:]/-}_${RUN_TAG}"

# "group:position" for every case folder that exists, sorted by length then id.
PAIRS=()
if [ -n "${CASES_OVERRIDE:-}" ]; then
    for tok in $CASES_OVERRIDE; do PAIRS+=("${tok/_/:}"); done
else
    for L in $LENGTHS; do
        while IFS= read -r id; do PAIRS+=("${L}:${id}"); done < <(
            ls -d "${BASE_PATH}/length${L}_"* 2>/dev/null | sed "s|.*/length${L}_||" | sort -n)
    done
fi

# SKIP_CASES="4_0 4_1 ... 4_18" (space-separated "L_id" tokens) drops those cases from the run.
# Ignored when CASES_OVERRIDE is set -- CASES_OVERRIDE already names exactly what to run.
if [ -z "${CASES_OVERRIDE:-}" ] && [ -n "${SKIP_CASES:-}" ]; then
    declare -A _skip
    for tok in $SKIP_CASES; do _skip["${tok/_/:}"]=1; done
    _kept=()
    for p in "${PAIRS[@]}"; do [ -z "${_skip[$p]:-}" ] && _kept+=("$p"); done
    echo "SKIP_CASES: dropping ${#_skip[@]} case(s), ${#PAIRS[@]} -> ${#_kept[@]}"
    PAIRS=("${_kept[@]}")
fi

echo "Total cases: ${#PAIRS[@]}  model=$MODEL  workers=$N_WORKERS"
if [ -n "${DRY_RUN:-}" ]; then
    for L in $LENGTHS; do
        n=0; for p in "${PAIRS[@]}"; do [ "${p%%:*}" = "$L" ] && n=$((n+1)); done
        echo "  length $L: $n cases"
    done
    echo "result dir : $RESULT_DIR"; echo "predict dir: $PREDICT_DIR"; echo "run logs   : $RUN_LOGS"
    exit 0
fi

source /home/asurite.ad.asu.edu/jrtandel/transchema/env/bin/activate
export BAT_MCTS_LOG_DIR="${RUN_LOGS}/mcts"
export BAT_LLM_LOG_DIR="${RUN_LOGS}/llm"

if [[ "$MODEL" == dmx-* ]]; then
    code=$(curl -s -m 10 -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/v1/chat/completions || true)
    if [ "$code" = "000" ] || [ -z "$code" ]; then
        echo "ERROR: $MODEL needs the SSH tunnel -- nothing is listening on localhost:8000." >&2
        echo "  run:  ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>" >&2
        exit 1
    fi
fi

echo "Result dir:  $RESULT_DIR"
echo "Predict dir: $PREDICT_DIR"
echo "Run logs:    $RUN_LOGS"
mkdir -p "$RUN_LOGS/workers"
pids=()
for ((i = 0; i < N_WORKERS; i++)); do
    chunk=()
    for ((j = i; j < ${#PAIRS[@]}; j += N_WORKERS)); do
        chunk+=("${PAIRS[$j]}")
    done
    if [ "${#chunk[@]}" -eq 0 ]; then
        continue
    fi
    echo "worker $i: ${#chunk[@]} case(s)"
    (
        for pair in "${chunk[@]}"; do
            group="${pair%%:*}"
            position="${pair##*:}"
            timeout "${CASE_TIMEOUT}s" python3 run_cases_iteratively.py \
                --length_type "$group" \
                --cases "$position" \
                --base_path "$BASE_PATH" \
                --result_dir "$RESULT_DIR" \
                --predict_dir "$PREDICT_DIR/g${group}_c${position}" \
                --validation autopipeline \
                --model_name "$MODEL" \
                || echo "[$(date '+%H:%M:%S')] case ${group}_${position}: TIMED OUT or FAILED (see above) -- continuing to the next case"
        done
    ) > "${RUN_LOGS}/workers/worker_${i}.log" 2>&1 &
    pids+=($!)
done

echo "Launched ${#pids[@]} workers, waiting..."
fail=0
for pid in "${pids[@]}"; do
    wait "$pid" || fail=1
done

echo "All workers finished (fail=$fail)."
echo "RESULT_DIR=$RESULT_DIR"
echo "PREDICT_DIR=$PREDICT_DIR"

python3 - "$PREDICT_DIR" "$RESULT_DIR" "$MODEL" "${#PAIRS[@]}" <<'PY'
import sys, glob, pandas as pd
pdir, rdir, model, expected = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
fs = glob.glob(f"{pdir}/*/master_results_*.csv")
if not fs:
    raise SystemExit(f"no master_results_*.csv under {pdir} -- check the worker logs")
d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
d["correct"] = d.accuracy == 1.0
n = int(d.correct.sum())
print(f"\nBAT {model}, github-pipelines: {n}/{expected} = {100 * n / expected:.1f}%  ({len(d)} cases have a score)")
print(d.groupby("length_type").correct.agg(["sum", "count"]).T.to_string())
left = glob.glob(f"{rdir}/length*/length*_*.json")
if len(d) != expected:
    print(f"WARNING: {expected - len(d)} of {expected} cases have no score; {len(left)} of them have a saved (unscored) result JSON "
          f"in {rdir} -- rerun BAT/rescore_unscored_cases.py for those; the rest crashed before saving.")
PY
