#!/bin/bash
# Host protection for long TreeMorpher batches: one HARD memory ceiling around ALL case scopes.
#
#   bash memory_guard.sh on [GB]   set it (default GB = 75% of RAM); also disables swap for the cases
#   bash memory_guard.sh off       remove it
#   bash memory_guard.sh status
#
# Why: without a ceiling a few memory-hungry cases (deep joins, multi-GB scratch CSVs) can fill RAM and push
# the machine into swap thrashing -- the whole server stalls (or systemd-oomd kills the whole tmux pane). With
# every case in its own systemd scope inside ablation.slice, hitting the ceiling makes the KERNEL kill the
# largest process in the slice (one case), and the server keeps running. The setting is runtime-only: it does
# not survive a reboot, so the batch script re-applies it on every start.
SLICE="${CASE_SLICE:-ablation.slice}"
cmd="${1:-status}"

prereq() {
    systemd-run --user --scope --quiet --slice="$SLICE" true >/dev/null 2>&1 \
        || { echo "memory_guard: 'systemd-run --user --scope' does not work here (no user systemd session?)" >&2; return 1; }
    grep -qw memory "/sys/fs/cgroup/user.slice/user-$(id -u).slice/user@$(id -u).service/cgroup.controllers" 2>/dev/null \
        || { echo "memory_guard: the memory cgroup controller is not delegated to your user manager" >&2; return 1; }
}

case "$cmd" in
  on)
    prereq || exit 1
    total_kb=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)
    gb="${2:-$(( total_kb * 75 / 100 / 1024 / 1024 ))}"
    [ "$gb" -ge 4 ] || { echo "memory_guard: computed limit ${gb}G is too small" >&2; exit 1; }
    systemctl --user set-property --runtime "$SLICE" MemoryMax="${gb}G" MemorySwapMax=0 || exit 1
    echo "memory_guard ON: $SLICE MemoryMax=${gb}G MemorySwapMax=0   (machine RAM: $(( total_kb / 1024 / 1024 )) GB)"
    ;;
  off)
    systemctl --user revert "$SLICE" 2>&1 | tail -1
    echo "memory_guard OFF"
    ;;
  status)
    systemctl --user show "$SLICE" -p MemoryMax -p MemorySwapMax -p MemoryCurrent 2>&1
    echo "RAM: $(free -g | awk '/^Mem:/ {print $2" GB total, "$3" GB used, "$7" GB available"}')"
    echo "oomd: $(systemctl is-active systemd-oomd 2>&1)"
    ;;
  *) echo "usage: bash memory_guard.sh on [GB] | off | status"; exit 2 ;;
esac
