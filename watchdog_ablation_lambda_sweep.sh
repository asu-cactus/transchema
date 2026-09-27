#!/bin/bash
# Standalone local watchdog for the w/o s_fd + w/o s_col reward-ablation batch.
# Runs independently of any Claude Code session, in its own tmux session. Every 30 min it checks
# that the BATCH PROCESS (run_ablation_lambda_sweep.sh) is actually running -- not merely that
# its tmux session exists (an idle session after a failed batch fooled the first version for ~6 h).
# If the process is gone and the log has no "ALL 4 STAGES COMPLETE", it recreates the tmux session
# and relaunches; the launchers' resume logic skips already-scored cases.
#
#     tmux new-session -d -s ablation_watchdog -c ~/transchema
#     tmux send-keys -t ablation_watchdog "bash watchdog_ablation_wofd_wocol.sh" C-m
# Stop it with: tmux kill-session -t ablation_watchdog   (does not stop the batch)

cd "$(dirname "$0")" || exit 1

JOB_SESSION="ablation_lambda_sweep"
BATCH_PATTERN="run_ablation_lambda_sweep\.sh"
LOG="logs_langraph/ablation_lambda_sweep_batch.log"
CHECK_INTERVAL=1800

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WATCHDOG] $1"; }
log "Watchdog started. Checking for the batch process every ${CHECK_INTERVAL}s."

while true; do
    if grep -q "ALL 4 STAGES COMPLETE" "$LOG" 2>/dev/null; then
        log "Batch log shows ALL 4 STAGES COMPLETE -- watchdog exiting."
        exit 0
    fi

    if pgrep -u "$(id -u)" -f "$BATCH_PATTERN" >/dev/null; then
        log "OK -- batch process running. Last log line: $(tail -1 "$LOG" 2>/dev/null)"
    else
        log "Batch process NOT running and no completion logged -- relaunching. Last log line: $(tail -1 "$LOG" 2>/dev/null)"
        tmux kill-session -t "$JOB_SESSION" 2>/dev/null
        tmux new-session -d -s "$JOB_SESSION" -c "$(pwd)"
        tmux send-keys -t "$JOB_SESSION" \
            "source env/bin/activate && bash run_ablation_lambda_sweep.sh 2>&1 | tee -a $LOG" C-m
        sleep 20
        if pgrep -u "$(id -u)" -f "$BATCH_PATTERN" >/dev/null; then
            log "Relaunched successfully."
        else
            log "ERROR: relaunch did not start a batch process."
        fi
    fi
    sleep "$CHECK_INTERVAL"
done
