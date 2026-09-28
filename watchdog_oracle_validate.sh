#!/bin/bash
# Standalone watchdog for the 4-stage oracle_validate.py sequence (reward-ablation Oracle
# metric: github_abl_wofd -> github_abl_wocol -> smartbuilding_v2_abl_wofd ->
# smartbuilding_v2_abl_wocol). If the oracle_validate tmux session or its process disappears
# (e.g. an accidental Ctrl+C from an attached terminal killing the pane) before the sequence
# logs ALL_ORACLE_RUNS_COMPLETE, this relaunches the exact same 4-stage command from scratch
# (oracle_validate.py has no per-case resume -- a relaunch redoes whichever stage was in
# progress; earlier fully-finished stages are untouched since each writes its own CSV).
#
#     tmux new-session -d -s oracle_watchdog -c ~/transchema
#     tmux send-keys -t oracle_watchdog "bash watchdog_oracle_validate.sh" C-m
# Stop it with: tmux kill-session -t oracle_watchdog   (does not stop the batch)

cd "$(dirname "$0")" || exit 1

JOB_SESSION="oracle_validate"
LOG="logs_langraph/oracle_sb_wocol.log"
CHECK_INTERVAL=300

CMD='source env/bin/activate && \
python3 oracle_validate.py --benchmark github --exp_name github_abl_wofd_dmx-gpt-oss-120b --workers 40 2>&1 | tee -a logs_langraph/oracle_github_wofd.log && \
python3 oracle_validate.py --benchmark github --exp_name github_abl_wocol_dmx-gpt-oss-120b --workers 40 2>&1 | tee -a logs_langraph/oracle_github_wocol.log && \
python3 oracle_validate.py --benchmark smart_building_v2 --exp_name smartbuilding_v2_abl_wofd_dmx-gpt-oss-120b --workers 40 2>&1 | tee -a logs_langraph/oracle_sb_wofd.log && \
python3 oracle_validate.py --benchmark smart_building_v2 --exp_name smartbuilding_v2_abl_wocol_dmx-gpt-oss-120b --workers 40 2>&1 | tee -a logs_langraph/oracle_sb_wocol.log && \
echo ALL_ORACLE_RUNS_COMPLETE'

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WATCHDOG] $1"; }
log "Watchdog started. Checking every ${CHECK_INTERVAL}s."

while true; do
    if grep -q "ALL_ORACLE_RUNS_COMPLETE" "$LOG" 2>/dev/null; then
        log "Sequence complete -- watchdog exiting."
        exit 0
    fi

    if pgrep -u "$(id -u)" -f "oracle_validate.py --benchmark" >/dev/null; then
        log "OK -- oracle_validate.py running."
    else
        log "oracle_validate.py NOT running and sequence not complete -- relaunching."
        tmux kill-session -t "$JOB_SESSION" 2>/dev/null
        tmux new-session -d -s "$JOB_SESSION" -c "$(pwd)"
        tmux set-option -t "$JOB_SESSION" remain-on-exit on
        tmux send-keys -t "$JOB_SESSION" "$CMD" C-m
        sleep 20
        if pgrep -u "$(id -u)" -f "oracle_validate.py --benchmark" >/dev/null; then
            log "Relaunched successfully."
        else
            log "ERROR: relaunch did not start a process."
        fi
    fi
    sleep "$CHECK_INTERVAL"
done
