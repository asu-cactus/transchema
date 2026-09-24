#!/usr/bin/env bash
# Runs the full smart_building v2 benchmark (105 cases) through auto_pipeline_join.py
# with 20-way parallelism: cases are split into 20 chunks, each chunk run as its
# own background process (own Postgres connection, own experiment_name/log dir),
# safe because every case creates/drops uniquely-named tables (sourceG_P_0,
# targetG_P) so there's no cross-process collision.
#
# Usage:  bash run_smartbuilding_v2_parallel.sh [MODEL]     (default gpt-4.1-mini)
#   e.g.  bash run_smartbuilding_v2_parallel.sh dmx-gpt-oss-120b
# dmx-* models go through the SSH tunnel to the Azure VM proxy (localhost:8000):
#   ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>
# Run ONE model at a time: the per-case Postgres tables have fixed names, so two
# concurrent runs (even of different models) would drop each other's tables.
set -euo pipefail

cd "$(dirname "$0")"
source /home/asurite.ad.asu.edu/jrtandel/transchema/env/bin/activate
export PGHOST=""
export PGUSER="$USER"

MANIFEST=/home/asurite.ad.asu.edu/jrtandel/transchema/autopipeline-benchmarks/smartbuilding-pipelines-v2-split/split_manifest.csv
N_WORKERS=20
MODEL="${1:-gpt-4.1-mini}"
RUN_TAG="smartbuilding_v2_full_105_${MODEL//[.:]/-}_$(date +%Y%m%d_%H%M%S)"

if [[ "$MODEL" == dmx-* ]]; then
    code=$(curl -s -m 10 -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/v1/chat/completions || true)
    if [ "$code" = "000" ] || [ -z "$code" ]; then
        echo "ERROR: $MODEL needs the SSH tunnel -- nothing is listening on localhost:8000." >&2
        echo "  run:  ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>" >&2
        exit 1
    fi
fi

mapfile -t CASES < <(tail -n +2 "$MANIFEST" | cut -d',' -f1 | sed 's/^length/Target/')
echo "Total cases: ${#CASES[@]}"

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
    echo "worker $i: ${#chunk[@]} cases -> $part_name (${chunk[*]})"
    python3 auto_pipeline_join.py \
        --benchmark smart_building_v2 \
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
echo "Result dirs:"
ls -d logs/${RUN_TAG}_part*_* 2>/dev/null

python3 - "$RUN_TAG" <<'PY'
import sys, glob, pandas as pd
tag = sys.argv[1]
fs = [f for f in glob.glob(f"logs/{tag}_part*_*/results.csv") if open(f).read().strip()]
if not fs:
    raise SystemExit("no results.csv files with data -- check logs/*_parts/worker_*.log")
d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
d["length"] = d.case.str.extract(r"length(\d+)_")[0].astype(int)
out = f"logs/{tag}_merged_results.csv"
d.to_csv(out, index=False)
print(f"\nSQLMorpher {d.model.iloc[0]}, smart_building_v2: {int(d.correct.sum())}/{len(d)} = {d.correct.mean():.1%}")
print(d.groupby("length").correct.agg(["sum", "count"]).T.to_string())
print(f"cases with an error (SQL/LLM failure, counted incorrect): {int(d.error.notna().sum())}")
if len(d) != 105:
    print(f"WARNING: expected 105 cases, got {len(d)}")
print("merged:", out)
PY
