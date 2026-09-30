#!/bin/bash
# Standalone watchdog for the chained 2-experiment queue on this server: no-static-hints
# (run_ablation_no_static_hints.sh) THEN equal-weights (run_ablation_equal_weights.sh), run
# back-to-back in one tmux pane. Every 30 min it checks whether the CHAIN's process is still
# running -- not merely that its tmux session exists. If it's gone and NEITHER experiment's
# completion marker is in its log yet, it relaunches the full chain command. This is safe to
# do repeatedly: run_ablation_no_static_hints.sh's own GitHub-side resume logic skips already-
# scored cases (its Smart Building phase restarts from scratch if interrupted mid-phase, same
# as every other 2-phase batch), and if no-static-hints already finished, its relaunch is a fast
# no-op pass before the chain proceeds into equal-weights.
#
#     tmux new-session -d -s ablation_watchdog -c ~/transchema
#     tmux send-keys -t ablation_watchdog "bash watchdog_ablation_queue.sh" C-m
# Stop it with: tmux kill-session -t ablation_watchdog   (does not stop the batch)

cd "$(dirname "$0")" || exit 1

JOB_SESSION="ablation_queue"
BATCH_PATTERN="run_ablation_no_static_hints\.sh|run_ablation_equal_weights\.sh"
LOG1="logs_langraph/ablation_no_static_hints_batch.log"
LOG2="logs_langraph/ablation_equal_weights_batch.log"
CHECK_INTERVAL=1800

CMD='source env/bin/activate && \
bash run_ablation_no_static_hints.sh 2>&1 | tee -a logs_langraph/ablation_no_static_hints_batch.log && \
bash run_ablation_equal_weights.sh 2>&1 | tee -a logs_langraph/ablation_equal_weights_batch.log && \
echo ABLATION_QUEUE_COMPLETE'

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WATCHDOG] $1"; }
log "Watchdog started. Checking every ${CHECK_INTERVAL}s."

while true; do
    if grep -q "ALL 2 STAGES COMPLETE" "$LOG2" 2>/dev/null; then
        log "Both experiments complete (equal-weights log shows ALL 2 STAGES COMPLETE) -- watchdog exiting."
        exit 0
    fi

    if pgrep -u "$(id -u)" -f "$BATCH_PATTERN" >/dev/null; then
        log "OK -- batch process running. Last line (no-static-hints): $(tail -1 "$LOG1" 2>/dev/null)  |  (equal-weights): $(tail -1 "$LOG2" 2>/dev/null)"
    else
        log "Batch process NOT running and queue not complete -- relaunching the chain. Last line (no-static-hints): $(tail -1 "$LOG1" 2>/dev/null)  |  (equal-weights): $(tail -1 "$LOG2" 2>/dev/null)"
        tmux kill-session -t "$JOB_SESSION" 2>/dev/null
        tmux new-session -d -s "$JOB_SESSION" -c "$(pwd)"
        tmux send-keys -t "$JOB_SESSION" "$CMD" C-m
        sleep 20
        if pgrep -u "$(id -u)" -f "$BATCH_PATTERN" >/dev/null; then
            log "Relaunched successfully."
        else
            log "ERROR: relaunch did not start a batch process."
        fi
    fi
    sleep "$CHECK_INTERVAL"
done
