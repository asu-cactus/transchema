#!/bin/bash
# Standalone local watchdog for the w/o s_fd + w/o s_col reward-ablation batch.
# Runs independently of any Claude Code session -- lives entirely in its own tmux
# session on this machine. Checks every 30 min whether run_ablation_reward_wofd_wocol.sh
# (in tmux session "ablation_wofd_wocol") is still alive; if it died without logging its
# own "ALL 4 STAGES COMPLETE", relaunches it in a fresh tmux session with the same
# command. run_github_mcts_dmx.sh / run_smartbuilding_v2_mcts20_dmx.sh's own resume logic
# (skip cases that already have a non-empty results_summary.csv) means a restart never
# redoes finished work.
#
#     cd ~/transchema
#     tmux new-session -d -s ablation_watchdog -c ~/transchema
#     tmux send-keys -t ablation_watchdog "bash watchdog_ablation_wofd_wocol.sh" C-m
#
# Stop it with: tmux kill-session -t ablation_watchdog
# (Killing the watchdog does NOT kill the batch itself -- that's a separate tmux session.)

cd "$(dirname "$0")" || exit 1

JOB_SESSION="ablation_wofd_wocol"
LOG="logs_langraph/ablation_wofd_wocol_batch.log"
CHECK_INTERVAL=1800   # 30 minutes

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WATCHDOG] $1"; }

log "Watchdog started. Checking session '$JOB_SESSION' every ${CHECK_INTERVAL}s."

while true; do
    if grep -q "ALL 4 STAGES COMPLETE" "$LOG" 2>/dev/null; then
        log "Batch log shows ALL 4 STAGES COMPLETE -- job finished. Watchdog exiting."
        exit 0
    fi

    if tmux has-session -t "$JOB_SESSION" 2>/dev/null; then
        log "OK -- '$JOB_SESSION' is alive. Last log line: $(tail -1 "$LOG" 2>/dev/null)"
    else
        log "'$JOB_SESSION' is NOT running and the batch did not log completion -- relaunching."
        source env/bin/activate
        tmux new-session -d -s "$JOB_SESSION" -c "$(pwd)"
        tmux send-keys -t "$JOB_SESSION" \
            "source env/bin/activate && bash run_ablation_reward_wofd_wocol.sh 2>&1 | tee -a $LOG" C-m
        sleep 10
        if tmux has-session -t "$JOB_SESSION" 2>/dev/null; then
            log "Relaunched successfully."
        else
            log "ERROR: relaunch failed -- '$JOB_SESSION' still not running after restart attempt."
        fi
    fi

    sleep "$CHECK_INTERVAL"
done
