#!/bin/bash
# For each model in MODELS, runs the smart_building_v2 105-case MCTS benchmark (all 15
# lengths, same case-discovery rule as run_smartbuilding_v2_mcts20_dmx.sh: any id with a
# case folder) in two phases:
#
#   Phase 1: same_leaf_stopping=5 (default), all 105 cases, MAX_JOBS=10
#   Phase 2: same_leaf_stopping=0 (disabled), ONLY the cases phase 1 got wrong, MAX_JOBS=10
#
# Models run strictly one after another -- both phases of dmx-deepseek-v4-flash complete
# before dmx-deepseek-v4-pro's phase 1 starts. This isn't a choice, it's a requirement:
# run_smartbuilding_v2_mcts20_dmx.sh refuses to start a second run (any model) while one
# is active, since concurrent MCTS runs write into the same benchmark case folders.
#
# Usage:
#     cd ~/transchema && source env/bin/activate
#     ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>   # other terminal
#     bash run_smartbuilding_v2_2phase_leafstop.sh
#
# Overrides:
#     MODELS="dmx-deepseek-v4-flash dmx-deepseek-v4-pro"   (default; order = run order)
#     RUN_TAG="mcts105_2phase"                             (default; a run timestamp is
#                                                            always appended -- see below)
#     MAX_JOBS=10                                          (default, both phases)
#     LENGTHS="1 2 3 ... 15"                               (default = full 105-case set)
#     CASE_TIMEOUT                                          forwarded to the inner script
#                                                            if already exported
#
# RUN_TAG always gets "_<launch timestamp>" appended, so every invocation of this script
# writes into brand-new result/log directories -- a previous run (whether an old run of
# this same script, or an unrelated experiment) can NEVER leak into phase 1's score or
# phase 2's failed-case list, because the glob that computes them is scoped to this run's
# own directory, which never existed before this launch.
#
# Result dirs (relative to Langraph/, per the inner script's convention):
#     results_langraph/smartbuilding_v2_<RUN_TAG>_<ts>_leafstop_<model>
#     results_langraph/smartbuilding_v2_<RUN_TAG>_<ts>_noleafstop_<model>   (phase-1 fails only)

cd "$(dirname "$0")" || exit 1

MODELS="${MODELS:-dmx-deepseek-v4-flash dmx-deepseek-v4-pro}"
RUN_TAG="${RUN_TAG:-mcts105_2phase}_$(date '+%Y%m%d_%H%M%S')"
MAX_JOBS="${MAX_JOBS:-10}"
LENGTHS="${LENGTHS:-1 2 3 4 5 6 7 8 9 10 11 12 13 14 15}"

log() { echo "[$(date '+%H:%M:%S')] [2PHASE] $1"; }
log "run tag for this launch: $RUN_TAG (own result dirs -- no prior run can interfere)"

# Reads one results dir's results_summary.csv files, keeping only the most-recently
# modified file per case_id (belt-and-suspenders against a case somehow being re-run
# within the SAME directory -- the fresh per-launch RUN_TAG above is what actually
# guarantees no cross-run interference).
STATUS_HELPER="$(mktemp)"
trap 'rm -f "$STATUS_HELPER"' EXIT
cat > "$STATUS_HELPER" <<'PY'
import sys, csv, glob, os

def latest_status(root):
    best = {}   # case_id -> (mtime, is_correct)
    for f in glob.glob(f"{root}/*/results_summary.csv"):
        mtime = os.path.getmtime(f)
        with open(f) as fh:
            for r in csv.DictReader(fh):
                cid = r.get("case_id") or r.get("id")
                if cid is None:
                    continue
                if cid not in best or mtime > best[cid][0]:
                    ic = r.get("is_correct", "").strip().lower() in ("true", "1")
                    best[cid] = (mtime, ic)
    return {cid: ic for cid, (_, ic) in best.items()}

mode = sys.argv[1]
if mode == "fails":
    d = latest_status(sys.argv[2])
    fails = sorted((cid for cid, ic in d.items() if not ic),
                   key=lambda x: tuple(int(v) for v in x.split("_")))
    print(" ".join(fails))
elif mode == "score":
    d = latest_status(sys.argv[2])
    print(f"{sum(d.values())}/{len(d)}")
elif mode == "combined":
    p1, p2 = latest_status(sys.argv[2]), latest_status(sys.argv[3])
    merged = dict(p1)
    merged.update(p2)  # phase 2 only re-ran the phase-1 fails -- this is the final per-case result
    print(f"{sum(merged.values())}/{len(merged)}")
PY

failed_cases_for() { python3 "$STATUS_HELPER" fails "$1"; }
score_for() { python3 "$STATUS_HELPER" score "$1"; }

SUMMARY=()

for MODEL in $MODELS; do
    log "===== $MODEL: phase 1 (same_leaf_stopping=5, all 105 cases, MAX_JOBS=$MAX_JOBS) ====="
    MODELS="$MODEL" RUN_TAG="${RUN_TAG}_leafstop" MAX_JOBS="$MAX_JOBS" SAME_LEAF_STOPPING=5 LENGTHS="$LENGTHS" \
        bash run_smartbuilding_v2_mcts20_dmx.sh || { log "$MODEL: phase 1 FAILED (preflight or fatal error) -- stopping"; exit 1; }

    p1_dir="Langraph/results_langraph/smartbuilding_v2_${RUN_TAG}_leafstop_${MODEL}"
    p1_score=$(score_for "$p1_dir")
    fails=$(failed_cases_for "$p1_dir")

    if [ -z "$fails" ]; then
        log "$MODEL: phase 1 = $p1_score, zero failures -- skipping phase 2"
        SUMMARY+=("$MODEL: phase1=$p1_score  phase2=skipped(no fails)  combined=$p1_score")
        continue
    fi

    n_fail=$(echo "$fails" | wc -w)
    log "$MODEL: phase 1 = $p1_score, $n_fail case(s) failed: $fails"
    log "===== $MODEL: phase 2 (same_leaf_stopping=0, retrying $n_fail failed case(s), MAX_JOBS=$MAX_JOBS) ====="
    MODELS="$MODEL" RUN_TAG="${RUN_TAG}_noleafstop" MAX_JOBS="$MAX_JOBS" SAME_LEAF_STOPPING=0 \
        CASES_OVERRIDE="$fails" bash run_smartbuilding_v2_mcts20_dmx.sh || { log "$MODEL: phase 2 FAILED (preflight or fatal error) -- stopping"; exit 1; }

    p2_dir="Langraph/results_langraph/smartbuilding_v2_${RUN_TAG}_noleafstop_${MODEL}"
    p2_score=$(score_for "$p2_dir")
    combined=$(python3 "$STATUS_HELPER" combined "$p1_dir" "$p2_dir")
    log "$MODEL: phase 1 = $p1_score, phase 2 (retried fails) = $p2_score, combined = $combined"
    SUMMARY+=("$MODEL: phase1=$p1_score  phase2(retried $n_fail)=$p2_score  combined=$combined")
done

echo
echo "================ TWO-PHASE SUMMARY ================"
for line in "${SUMMARY[@]}"; do echo "  $line"; done
