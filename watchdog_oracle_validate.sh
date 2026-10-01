#!/bin/bash
# Standalone watchdog for the 4-stage oracle_validate.py sequence (reward-ablation Oracle
# metric: github_abl_wofd -> github_abl_wocol -> smartbuilding_v2_abl_wofd ->
# smartbuilding_v2_abl_wocol). If the oracle_validate_batch.service unit stops before the
# sequence logs ALL_ORACLE_RUNS_COMPLETE, this relaunches the exact same 4-stage command.
# Cheap now: oracle_validate.py has per-case resume (reads the stage's existing
# <exp>_oracle.csv and skips cases already recorded there), so a relaunch only redoes
# whatever a stage hadn't finished yet, not the whole stage.
#
# Root cause found 2026-09-28 (after two wrong turns -- accidental Ctrl+C, then a PSI/pressure
# theory -- both ruled out by `systemctl --user status oracle_validate_batch.service`, which
# gave the real answer directly: "Result: oom-kill", with `MemoryPeak` on ablation.slice
# landing right at `MemoryMax` both at 40 and at 8 workers -- i.e. NOT scaling with worker
# count, so not a concurrency/churn problem. It's compare_tables()/compare_series()
# (validation/autopipeline_match.py): a pure-Python nested for-col_target/for-col_generate
# loop, O(rows * cols^2). This project's own benchmarks are heavy-tailed (p95 ~50k rows, max
# 13.2M) -- production validates once per case, Oracle validates once per candidate script,
# multiplying the cost until one pathological case's comparison blew past the 46G ceiling and
# took the whole cgroup (every worker) down together. oracle_validate.py now skips any case
# whose ground truth exceeds 50k rows with a clear note instead of risking this again.
#
# Runs the job as a systemd --user *service* (systemd-run --unit=..., not --scope and not
# tmux): a scope/tmux pane is still tied to the invoking login session and can be torn down
# with it; a service lives under the persistent user@<uid>.service (kept alive by lingering),
# fully decoupled from any specific session. `systemctl --user status` on it gives a real
# Result= reason when it stops, instead of a bare "Terminated" with no diagnosis.
#
#     tmux new-session -d -s oracle_watchdog -c ~/transchema
#     tmux send-keys -t oracle_watchdog "bash watchdog_oracle_validate.sh" C-m
# Stop it with: tmux kill-session -t oracle_watchdog   (does not stop the batch service)
# Check the batch directly: systemctl --user status oracle_validate_batch.service
#
# Bug fixed 2026-10-01 (found while running the rewfam variant of this watchdog): the chain's
# final `echo ALL_ORACLE_RUNS_COMPLETE` used to go nowhere -- only the preceding
# `python3 ... | tee -a <file>` commands were piped anywhere, so the bare trailing echo after
# the last && just went to the service's own stdout (journal), never into any file this script
# greps. The completion check could never find it, so a FULLY FINISHED run looked identical to
# "still running" and the watchdog kept relaunching forever -- harmlessly (each relaunch just
# resumes-and-skips everything in seconds and exits 0 again) but endlessly. Now redirected into
# the last stage's own log file.

cd "$(dirname "$0")" || exit 1

UNIT="oracle_validate_batch"
LOG="logs_langraph/oracle_sb_wocol.log"
CHECK_INTERVAL=60
ORACLE_WORKERS="${ORACLE_WORKERS:-8}"

CMD="source env/bin/activate && \\
python3 oracle_validate.py --benchmark github --exp_name github_abl_wofd_dmx-gpt-oss-120b --workers $ORACLE_WORKERS 2>&1 | tee -a logs_langraph/oracle_github_wofd.log && \\
python3 oracle_validate.py --benchmark github --exp_name github_abl_wocol_dmx-gpt-oss-120b --workers $ORACLE_WORKERS 2>&1 | tee -a logs_langraph/oracle_github_wocol.log && \\
python3 oracle_validate.py --benchmark smart_building_v2 --exp_name smartbuilding_v2_abl_wofd_dmx-gpt-oss-120b --workers $ORACLE_WORKERS 2>&1 | tee -a logs_langraph/oracle_sb_wofd.log && \\
python3 oracle_validate.py --benchmark smart_building_v2 --exp_name smartbuilding_v2_abl_wocol_dmx-gpt-oss-120b --workers $ORACLE_WORKERS 2>&1 | tee -a logs_langraph/oracle_sb_wocol.log && \\
echo ALL_ORACLE_RUNS_COMPLETE >> logs_langraph/oracle_sb_wocol.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WATCHDOG] $1"; }
log "Watchdog started. Checking every ${CHECK_INTERVAL}s. Workers=${ORACLE_WORKERS}."

while true; do
    if grep -q "ALL_ORACLE_RUNS_COMPLETE" "$LOG" 2>/dev/null; then
        log "Sequence complete -- watchdog exiting."
        exit 0
    fi

    STATE=$(systemctl --user show "$UNIT.service" -p ActiveState --value 2>/dev/null)
    if [ "$STATE" = "active" ]; then
        log "OK -- $UNIT.service active."
    else
        RESULT=$(systemctl --user show "$UNIT.service" -p Result --value 2>/dev/null)
        log "$UNIT.service state=${STATE:-none} result=${RESULT:-n/a} -- relaunching."
        systemctl --user reset-failed "$UNIT.service" 2>/dev/null
        bash memory_guard.sh on
        systemd-run --user --unit="$UNIT" --slice=ablation.slice --working-directory="$(pwd)" bash -c "$CMD"
        sleep 10
        NEW_STATE=$(systemctl --user show "$UNIT.service" -p ActiveState --value 2>/dev/null)
        if [ "$NEW_STATE" = "active" ]; then
            log "Relaunched successfully."
        else
            log "ERROR: relaunch did not reach active state (state=$NEW_STATE)."
        fi
    fi
    sleep "$CHECK_INTERVAL"
done
