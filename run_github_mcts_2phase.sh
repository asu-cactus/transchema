#!/bin/bash
# TreeMorpher (Langraph/mcts_search.py) on the GitHub-pipelines benchmark, in two phases, for ONE model:
#
#   Phase 1: early leaf stopping ON  (same_leaf_stopping=5), every case
#   Phase 2: early leaf stopping OFF (same_leaf_stopping=0), ONLY the cases phase 1 did not solve
#            (including cases that produced no result); launched automatically when phase 1 ends.
#
# Both phases are run_github_mcts_dmx.sh underneath: curated-pipeline RAG on, det_score_value reward, 40 iterations,
# --data_split training, per-length --max_depth, 600s case timeout, MAX_JOBS in flight (a finished case frees its slot).
#
#     cd ~/transchema && source env/bin/activate
#     bash run_github_mcts_2phase.sh                                   # default MODEL=o4-mini (OpenAI API, needs $OPENAI_API_KEY)
#     MODEL=dmx-deepseek-v4-pro MAX_JOBS=15 bash run_github_mcts_2phase.sh   # DMX model: needs the SSH tunnel to localhost:8000
#
# Overrides:
#     MODEL=o4-mini                one model (a dmx-* model needs the tunnel; anything else needs its API key)
#     LENGTHS="1 2 3 4 5 6 9"      MAX_JOBS=20      RUN_TAG=<tag>      DRY_RUN=1 (print the plan, no LLM calls)
#     ONLY_LIST_FAILED=1           print the cases phase 1 (RUN_TAG) did not solve, then exit
#     SKIP_GUARD_PHASE1=1          also skip the "another MCTS run is active" check for phase 1 (phase 2 always skips it: the
#                                  phase-1 launcher's own leftover child processes can still be alive when it hands over)
#
# NOTE: o4-mini is a PAID API. From 113 earlier o4-mini MCTS case results the mean is ~$0.30 per case (median $0.17, p90 $0.66),
# so phase 1 on 698 cases is roughly $120-460 (about $200) and phase 2 about $75 for ~250 retried cases.
#
# Result dirs (relative to Langraph/results_langraph/), logs under logs_langraph/ (tokens are in the MCTS logs):
#     github_<RUN_TAG>_leafstop_<model>      github_<RUN_TAG>_noleafstop_<model>   (phase-2 cases only)
# Re-running with the same RUN_TAG resumes each phase (finished cases are skipped).

cd "$(dirname "$0")" || exit 1

MODEL="${MODEL:-o4-mini}"
RUN_TAG="${RUN_TAG:-gh2p_$(date '+%Y%m%d_%H%M%S')}"
LENGTHS="${LENGTHS:-1 2 3 4 5 6 9}"
MAX_JOBS="${MAX_JOBS:-20}"
P1="${RUN_TAG}_leafstop"
P2="${RUN_TAG}_noleafstop"

log() { echo "[$(date '+%H:%M:%S')] [2PHASE-GH] $1"; }

# "L_id" of every case phase 1 did not solve: all case folders for LENGTHS minus the ones with a correct result.
failed_cases() {
    python3 - "$P1" "$MODEL" "$LENGTHS" <<'PY'
import csv, glob, os, sys
tag, model, lengths = sys.argv[1], sys.argv[2], sys.argv[3].split()
expected = []
for L in lengths:
    for d in glob.glob(f"autopipeline-benchmarks/github-pipelines/length{L}_*"):
        expected.append((int(L), int(os.path.basename(d).split("_")[1])))
solved = set()
for f in glob.glob(f"Langraph/results_langraph/github_{tag}_{model}/*/results_summary.csv"):
    for r in csv.DictReader(open(f)):
        if (r.get("is_correct") or "").strip().lower() in ("true", "1"):
            solved.add(r["case_id"])
print(" ".join(f"{L}_{c}" for L, c in sorted(expected) if f"{L}_{c}" not in solved))
PY
}

if [ -n "${ONLY_LIST_FAILED:-}" ]; then failed_cases; exit 0; fi

if [[ "$MODEL" != dmx-* ]] && [ -z "${OPENAI_API_KEY:-}" ] && [ -z "${DRY_RUN:-}" ]; then
    echo "ERROR: MODEL=$MODEL is not a dmx-* model and \$OPENAI_API_KEY is not set." >&2
    exit 1
fi

if [ -n "${DRY_RUN:-}" ]; then
    echo "MODEL=$MODEL  RUN_TAG=$RUN_TAG  MAX_JOBS=$MAX_JOBS  LENGTHS=$LENGTHS"
    echo "phase 1 -> Langraph/results_langraph/github_${P1}_${MODEL}   (same_leaf_stopping=5)"
    echo "phase 2 -> Langraph/results_langraph/github_${P2}_${MODEL}   (same_leaf_stopping=0, only the cases phase 1 did not solve)"
    MODELS="$MODEL" RUN_TAG="$P1" LENGTHS="$LENGTHS" DRY_RUN=1 bash run_github_mcts_dmx.sh | sed -n 1,2p
    exit 0
fi

log "===== $MODEL: phase 1 (same_leaf_stopping=5, all cases, MAX_JOBS=$MAX_JOBS) -- RUN_TAG=$RUN_TAG ====="
MODELS="$MODEL" RUN_TAG="$P1" LENGTHS="$LENGTHS" MAX_JOBS="$MAX_JOBS" SAME_LEAF_STOPPING=5 SKIP_GUARD="${SKIP_GUARD_PHASE1:-}" \
    bash run_github_mcts_dmx.sh || { log "phase 1 launcher exited with an error (preflight or fatal) -- stopping"; exit 1; }

fails=$(failed_cases)
n_fail=$(echo "$fails" | wc -w)
n_all=$(python3 - "$LENGTHS" <<'PY'
import glob, sys
print(sum(len(glob.glob(f"autopipeline-benchmarks/github-pipelines/length{L}_*")) for L in sys.argv[1].split()))
PY
)
log "phase 1 done: $((n_all - n_fail))/$n_all solved, $n_fail did not solve (or produced no result)"
if [ "$n_fail" -eq 0 ]; then
    log "nothing left to retry -- skipping phase 2"
    exit 0
fi

log "===== $MODEL: phase 2 (same_leaf_stopping=0, retrying the $n_fail unsolved cases, MAX_JOBS=$MAX_JOBS) ====="
MODELS="$MODEL" RUN_TAG="$P2" MAX_JOBS="$MAX_JOBS" SAME_LEAF_STOPPING=0 CASES_OVERRIDE="$fails" SKIP_GUARD=1 \
    bash run_github_mcts_dmx.sh || { log "phase 2 launcher exited with an error -- phase-1 results are intact"; exit 1; }

python3 - "$P1" "$P2" "$MODEL" "$n_all" <<'PY'
import csv, glob, sys
p1, p2, model, n_all = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
def solved(tag):
    s = set()
    for f in glob.glob(f"Langraph/results_langraph/github_{tag}_{model}/*/results_summary.csv"):
        for r in csv.DictReader(open(f)):
            if (r.get("is_correct") or "").strip().lower() in ("true", "1"):
                s.add(r["case_id"])
    return s
a, b = solved(p1), solved(p2)
print(f"\n================ TWO-PHASE SUMMARY ({model}, GitHub, {n_all} cases) ================")
print(f"  phase 1 (leaf stopping 5):        {len(a)}/{n_all} = {100*len(a)/n_all:.1f}%   (/700: {100*len(a)/700:.1f}%)")
print(f"  phase 2 recovered (leaf stop 0):  +{len(b - a)}")
print(f"  combined:                         {len(a | b)}/{n_all} = {100*len(a | b)/n_all:.1f}%   (/700: {100*len(a | b)/700:.1f}%)")
PY
