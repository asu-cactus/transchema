#!/bin/bash
# Standalone local watchdog for the no-static-hints ablation batch (run_ablation_no_static_hints.sh:
# GitHub then Smart Building, RAG on, two-phase, single config). Runs independently of any
# Claude Code session, in its own tmux session. Every 30 min it checks that the BATCH PROCESS is
# actually running -- not merely that its tmux session exists. If the process is gone and the log
# has no "ALL 2 STAGES COMPLETE", it recreates the tmux session and relaunches; the 2-phase
# wrappers' own GitHub-side resume logic skips already-scored cases (Smart Building restarts its
# current phase from scratch if interrupted mid-phase -- see run_smartbuilding_v2_2phase_leafstop.sh's
# own header).
#
#     tmux new-session -d -s ablation_watchdog -c ~/transchema
#     tmux send-keys -t ablation_watchdog "bash watchdog_ablation_no_static_hints.sh" C-m
# Stop it with: tmux kill-session -t ablation_watchdog   (does not stop the batch)

cd "$(dirname "$0")" || exit 1

JOB_SESSION="ablation_no_static_hints"
BATCH_PATTERN="run_ablation_no_static_hints\.sh"
LOG="logs_langraph/ablation_no_static_hints_batch.log"
CHECK_INTERVAL=1800

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WATCHDOG] $1"; }
log "Watchdog started. Checking for the batch process every ${CHECK_INTERVAL}s."

while true; do
    if grep -q "ALL 2 STAGES COMPLETE" "$LOG" 2>/dev/null; then
        log "Batch log shows ALL 2 STAGES COMPLETE -- watchdog exiting."
        exit 0
    fi

    if pgrep -u "$(id -u)" -f "$BATCH_PATTERN" >/dev/null; then
        log "OK -- batch process running. Last log line: $(tail -1 "$LOG" 2>/dev/null)"
    else
        log "Batch process NOT running and no completion logged -- relaunching. Last log line: $(tail -1 "$LOG" 2>/dev/null)"
        tmux kill-session -t "$JOB_SESSION" 2>/dev/null
        tmux new-session -d -s "$JOB_SESSION" -c "$(pwd)"
        tmux send-keys -t "$JOB_SESSION" \
            "source env/bin/activate && bash run_ablation_no_static_hints.sh 2>&1 | tee -a $LOG" C-m
        sleep 20
        if pgrep -u "$(id -u)" -f "$BATCH_PATTERN" >/dev/null; then
            log "Relaunched successfully."
        else
            log "ERROR: relaunch did not start a batch process."
        fi
    fi
    sleep "$CHECK_INTERVAL"
done
