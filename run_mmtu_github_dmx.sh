#!/bin/bash
# MMTU baseline (Transform-by-output-target-schema, one-shot prompt) on the GitHub-pipelines
# benchmark, for a Microsoft DMX model -- same as run_mmtu_sb_v2_dmx.sh, pointed at GitHub.
#
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_mmtu_github_dmx.sh
#
# MMTU's curated set holds 672 of the 698 GitHub cases (L1 98, L2 100, L3 95, L4 94, L5 92,
# L6 97, L9 96). Cases MMTU does not contain are counted as INCORRECT in the 698-case accuracy
# printed at the end (the per-length lines also show the MMTU-only count).
#
# Overrides:
#     MODEL="dmx-gpt-oss-120b"   (default; any dmx-* model works)
#     N_PARALLEL=15              concurrent LLM requests through the proxy
#     LENGTH=""                  set to e.g. 1 to run/score only one length bucket
#     EVAL_WORKERS=4             parallel evaluator workers (each case runs in its own sandbox)
#     EVAL_ONLY=1                skip the LLM queries and only (re)score existing responses
#     DRY_RUN=1                  print what would run (row counts) and exit; no LLM calls
#
# Resumable: run_openai_task.py skips rows that already have a non-empty response in the result
# file, so rerunning after a crash or failed requests only queries the missing/empty ones.
#
# Output (relative to MMTU/):
#     results_github_dmx/mmtu.<model>.result.jsonl   raw model responses
#     eval_github_dmx_<model>/<model>_details.csv    per-case is_correct + reason
#     eval_github_dmx_<model>/<model>_summary.csv

cd "$(dirname "$0")" || exit 1
R=$PWD

MODEL="${MODEL:-dmx-gpt-oss-120b}"
N_PARALLEL="${N_PARALLEL:-15}"
LENGTH="${LENGTH:-}"
EVAL_WORKERS="${EVAL_WORKERS:-4}"
EVAL_ONLY="${EVAL_ONLY:-}"
TAG="${MODEL//./-}"; TAG="${TAG//:/-}"      # same sanitising run_openai_task.py applies

if [ -n "${DRY_RUN:-}" ]; then
    python3 - "$LENGTH" <<'PY'
import json, re, sys, collections
want = sys.argv[1]
c = collections.Counter()
for l in open("MMTU/mmtu.jsonl"):
    r = json.loads(l)
    if r.get("task") == "Transform-by-output-target-schema" and r.get("dataset") == "github-pipelines":
        m = re.match(r"length(\d+)_", json.loads(r["metadata"]).get("test_case", ""))
        if m and (not want or m.group(1) == want):
            c[int(m.group(1))] += 1
print("MMTU github-pipelines rows to query:", sum(c.values()), dict(sorted(c.items())))
PY
    echo "MODEL=$MODEL N_PARALLEL=$N_PARALLEL EVAL_WORKERS=$EVAL_WORKERS"
    exit 0
fi

if ! python3 -c "import transformers" 2>/dev/null; then
    echo "ERROR: venv not active (transformers missing). run:  source env/bin/activate" >&2
    exit 1
fi

# Evaluator sandboxes are written per eval run; refuse to start on a nearly-full disk.
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

    HF_HUB_OFFLINE=1 python3 MMTU/run_openai_task.py \
        --task        Transform-by-output-target-schema \
        --dataset     github-pipelines \
        --mmtu_jsonl  MMTU/mmtu.jsonl \
        --output_dir  MMTU/results_github_dmx \
        --model       "$MODEL" \
        --n_parallel  "$N_PARALLEL" \
        ${LENGTH:+--length "$LENGTH"} \
        || { echo "run_openai_task.py failed" >&2; exit 1; }
fi

RESULT="$R/MMTU/results_github_dmx/mmtu.${TAG}.result.jsonl"
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
    --data_root "$R/autopipeline-benchmarks/github-pipelines" \
    ${LENGTH:+--length "$LENGTH"} --workers "$EVAL_WORKERS" --timeout 60 \
    --output_dir "$R/MMTU/eval_github_dmx_${TAG}" 2>&1 | grep -vE "Evaluating:|it/s"

# Remove only the sandbox this evaluation created.
after=$(ls -d "$R"/MMTU/tmp_exec/autopipeline_eval_* 2>/dev/null | sort)
comm -13 <(echo "$before") <(echo "$after") | xargs -r rm -rf

python3 - "$R/MMTU/eval_github_dmx_${TAG}/${TAG}_details.csv" "$MODEL" <<'PY'
import sys, pandas as pd
try:
    d = pd.read_csv(sys.argv[1])
except FileNotFoundError:
    raise SystemExit(f"no details CSV at {sys.argv[1]} -- check disk space (df -h /)")
n = int(d.is_correct.sum())
print(f"\nMMTU {sys.argv[2]}, github-pipelines: {n}/{len(d)} correct of the {len(d)} cases MMTU contains; "
      f"{n}/698 = {100 * n / 698:.1f}% of all 698 GitHub cases (cases MMTU lacks count as incorrect)")
for L in sorted(d.length.unique()):
    x = d[d.length == L]
    print(f"  L{L:<3} {int(x.is_correct.sum())}/{len(x)}")
print("\nreasons:", d.reason.value_counts().to_dict())
PY
