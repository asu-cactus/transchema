#!/bin/bash
# Standalone watchdog for the 6-stage oracle_validate.py sequence over the reward-function-
# family ablation (bat_reward, ap_reward, llm_confidence x GitHub + Smart Building). Same
# mechanism as watchdog_oracle_validate.sh (see that file's header for the full root-cause
# writeup: real OOM-kills from pathological-sized cases, fixed in oracle_validate.py via
# row-count guards + a per-worker RLIMIT_AS cap, not a concurrency/churn problem). Runs the
# job as a systemd --user *service* (not tmux/scope -- those stay tied to the invoking login
# session and can be torn down with it; a service lives under the persistent
# user@<uid>.service, kept alive by lingering).
#
#     tmux new-session -d -s oracle_watchdog -c ~/transchema
#     tmux send-keys -t oracle_watchdog "bash watchdog_oracle_validate_rewfam.sh" C-m
# Stop it with: tmux kill-session -t oracle_watchdog   (does not stop the batch service)
# Check the batch directly: systemctl --user status oracle_validate_batch_rewfam.service
#
# Bug fixed 2026-10-01: the chain's final `echo ALL_ORACLE_RUNS_COMPLETE` used to go nowhere
# (only the preceding `python3 ... | tee -a <file>` commands were piped anywhere -- the bare
# trailing echo after the last && just went to the service's own stdout, captured by the
# journal, never into any file this script greps). The completion check below could never
# find it, so a FULLY FINISHED run looked identical to "still running" and the watchdog kept
# relaunching forever -- harmlessly (each relaunch just resumes-and-skips everything in
# seconds and exits 0 again) but endlessly. Now redirected into the last stage's own log file.

cd "$(dirname "$0")" || exit 1

UNIT="oracle_validate_batch_rewfam"
LOG="logs_langraph/oracle_sb_rewfam_conf.log"
CHECK_INTERVAL=60
ORACLE_WORKERS="${ORACLE_WORKERS:-8}"

CMD="source env/bin/activate && \\
python3 oracle_validate.py --benchmark github --exp_name github_abl_rewfam_bat_gh_dmx-gpt-oss-120b --workers $ORACLE_WORKERS 2>&1 | tee -a logs_langraph/oracle_github_rewfam_bat.log && \\
python3 oracle_validate.py --benchmark smart_building_v2 --exp_name smartbuilding_v2_abl_rewfam_bat_sb_dmx-gpt-oss-120b --workers $ORACLE_WORKERS 2>&1 | tee -a logs_langraph/oracle_sb_rewfam_bat.log && \\
python3 oracle_validate.py --benchmark github --exp_name github_abl_rewfam_ap_gh_dmx-gpt-oss-120b --workers $ORACLE_WORKERS 2>&1 | tee -a logs_langraph/oracle_github_rewfam_ap.log && \\
python3 oracle_validate.py --benchmark smart_building_v2 --exp_name smartbuilding_v2_abl_rewfam_ap_sb_dmx-gpt-oss-120b --workers $ORACLE_WORKERS 2>&1 | tee -a logs_langraph/oracle_sb_rewfam_ap.log && \\
python3 oracle_validate.py --benchmark github --exp_name github_abl_rewfam_conf_gh_dmx-gpt-oss-120b --workers $ORACLE_WORKERS 2>&1 | tee -a logs_langraph/oracle_github_rewfam_conf.log && \\
python3 oracle_validate.py --benchmark smart_building_v2 --exp_name smartbuilding_v2_abl_rewfam_conf_sb_dmx-gpt-oss-120b --workers $ORACLE_WORKERS 2>&1 | tee -a logs_langraph/oracle_sb_rewfam_conf.log && \\
echo ALL_ORACLE_RUNS_COMPLETE >> logs_langraph/oracle_sb_rewfam_conf.log"

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
