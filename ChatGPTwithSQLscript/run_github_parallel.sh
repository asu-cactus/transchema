#!/usr/bin/env bash
# SQLMorpher (auto_pipeline_join.py, the ChatGPT+SQL baseline) on the GitHub-pipelines benchmark
# (698 cases: L1 100, L2 100, L3 100, L4 100, L5 98, L6 99, L9 101; ids have gaps, so the case list
# is read from the folders on disk). Same worker pattern as run_smartbuilding_v2_parallel.sh: the
# cases are split round-robin across N_WORKERS background processes, each with its own Postgres
# connection and log dir. Safe because every case creates/drops uniquely-named tables.
#
# Usage:  bash run_github_parallel.sh [MODEL]      (default dmx-gpt-oss-120b)
#   e.g.  bash run_github_parallel.sh dmx-deepseek-v4-flash
# dmx-* models go through the SSH tunnel to the Azure VM proxy (localhost:8000):
#   ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>
#
# Overrides:  N_WORKERS=15  LENGTHS="1 2 3 4 5 6 9"  CASES_OVERRIDE="Target4_5 ..."  DRY_RUN=1 (print the case counts and exit)
#
# Run ONE SQLMorpher run at a time: the per-case Postgres tables have fixed names, so two
# concurrent runs (even for different models) would drop each other's tables.
set -euo pipefail

cd "$(dirname "$0")"
DRY_RUN="${DRY_RUN:-}"
BENCH=/home/asurite.ad.asu.edu/jrtandel/transchema/autopipeline-benchmarks/github-pipelines
N_WORKERS="${N_WORKERS:-15}"
LENGTHS="${LENGTHS:-1 2 3 4 5 6 9}"
MODEL="${1:-dmx-gpt-oss-120b}"
RUN_TAG="github_698_${MODEL//[.:]/-}_$(date +%Y%m%d_%H%M%S)"

# "Target<L>_<id>" for every case folder that exists, sorted by length then id.
CASES=()
for L in $LENGTHS; do
    while IFS= read -r id; do CASES+=("Target${L}_${id}"); done < <(
        ls -d "${BENCH}/length${L}_"* 2>/dev/null | sed "s|.*/length${L}_||" | sort -n)
done
# CASES_OVERRIDE="Target4_5 Target9_12 ..." runs only those (e.g. to redo cases a crashed run lost).
if [ -n "${CASES_OVERRIDE:-}" ]; then
    CASES=($CASES_OVERRIDE)
fi
echo "Total cases: ${#CASES[@]}  model=$MODEL  workers=$N_WORKERS  run_tag=$RUN_TAG"
if [ -n "$DRY_RUN" ]; then
    for L in $LENGTHS; do
        n=0; for c in "${CASES[@]}"; do [[ "$c" == Target${L}_* ]] && n=$((n+1)); done
        echo "  length $L: $n cases"
    done
    exit 0
fi

source /home/asurite.ad.asu.edu/jrtandel/transchema/env/bin/activate
export PGHOST=""
export PGUSER="$USER"

if [[ "$MODEL" == dmx-* ]]; then
    code=$(curl -s -m 10 -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/v1/chat/completions || true)
    if [ "$code" = "000" ] || [ -z "$code" ]; then
        echo "ERROR: $MODEL needs the SSH tunnel -- nothing is listening on localhost:8000." >&2
        echo "  run:  ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>" >&2
        exit 1
    fi
fi

mkdir -p "logs/${RUN_TAG}_parts"
pids=()
for ((i = 0; i < N_WORKERS; i++)); do
    chunk=()
    for ((j = i; j < ${#CASES[@]}; j += N_WORKERS)); do
        chunk+=("${CASES[$j]}")
    done
    if [ "${#chunk[@]}" -eq 0 ]; then
        continue
    fi
    part_name="${RUN_TAG}_part$(printf '%02d' "$i")"
    echo "worker $i: ${#chunk[@]} cases -> $part_name"
    python3 auto_pipeline_join.py \
        --benchmark autopipeline \
        --cases "${chunk[@]}" \
        --validation autopipeline \
        --experiment_name "$part_name" \
        --model "$MODEL" \
        > "logs/${RUN_TAG}_parts/worker_${i}.log" 2>&1 &
    pids+=($!)
done

echo "Launched ${#pids[@]} workers, waiting..."
fail=0
for pid in "${pids[@]}"; do
    wait "$pid" || fail=1
done

echo "All workers finished (fail=$fail)."
echo "RUN_TAG=${RUN_TAG}" > "logs/${RUN_TAG}_parts/run_tag.env"

python3 - "$RUN_TAG" "${#CASES[@]}" <<'PY'
import sys, glob, pandas as pd
tag, expected = sys.argv[1], int(sys.argv[2])
fs = [f for f in glob.glob(f"logs/{tag}_part*_*/results.csv") if open(f).read().strip()]
if not fs:
    raise SystemExit("no results.csv files with data -- check logs/*_parts/worker_*.log")
d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
d["length"] = d.case.str.extract(r"length(\d+)_")[0].astype(int)
out = f"logs/{tag}_merged_results.csv"
d.to_csv(out, index=False)
n = int(d.correct.sum())
print(f"\nSQLMorpher {d.model.iloc[0]}, github-pipelines: {n}/{expected} = {100 * n / expected:.1f}%  ({len(d)} cases have a result)")
print(d.groupby("length").correct.agg(["sum", "count"]).T.to_string())
print(f"cases with an error (SQL/LLM failure, counted incorrect): {int(d.error.notna().sum())}")
if len(d) != expected:
    print(f"WARNING: expected {expected} cases, got {len(d)} -- see the worker logs.")
print("merged:", out)
PY
