"""
analyze_o4mini_earlystop_cost_latency.py
=========================================
Mine avg cost / avg latency per case for the o4-mini + early-stopping
HYBRID-failed retry experiment (run_o4mini_earlystop_hybrid_failed.sh).

No results_summary.csv files exist for this experiment (checked: all empty),
so cost/latency is mined directly from the MCTS log for every case:
  - cost   = sum of all `Cost of the query : {'total_cost': X}` lines
  - latency = last_log_timestamp - first_log_timestamp (seconds)

True errors (0 cost lines -> no LLM calls ever completed, nothing to mine)
are excluded. Everything else (including cases that hit the 600s per-case
timeout and got recovered mid-query, which show up as logs with no
"Total queries" trailer line) IS included, per prior convention: those
cases still contributed a valid accuracy result, so their cost/latency
should count too.
"""
import glob
import re
from pathlib import Path
from datetime import datetime

L1_CASES = [8, 22, 24, 44, 54, 64, 75, 85, 86, 89, 90, 91, 93, 95, 97, 99]
L4_CASES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
            22, 23, 24, 28, 29, 30, 35, 36, 37, 40, 43, 45, 46, 47, 48, 49, 50, 51, 52,
            53, 58, 60, 61, 62, 63, 64, 68, 70, 71, 73, 84, 86, 87, 92, 93, 94, 96, 97,
            98, 99]
L9_CASES = [1, 3, 4, 13, 15, 16, 19, 20, 21, 22, 23, 24, 27, 29, 35, 36, 38, 40, 41, 42,
            43, 44, 45, 46, 62, 67, 68, 69, 70, 71, 72, 73, 74]

TS_RE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),(\d{3})")
COST_RE = re.compile(r"Cost of the query : \{'total_cost': ([0-9.eE+-]+)")


def log_dir_for(length):
    return f"logs_langraph/o4mini_earlystop_hybrid_failed_l{length}"


def parse_ts(line):
    m = TS_RE.match(line)
    if not m:
        return None
    return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")


def mine_case(length, case_num):
    d = Path(log_dir_for(length)) / f"cases_c{case_num}"
    files = sorted(d.glob("*.log")) if d.exists() else []
    if not files:
        return None
    log_file = files[-1]
    lines = log_file.read_text(errors="ignore").splitlines()

    total_cost = 0.0
    n_cost_lines = 0
    first_ts = last_ts = None
    for line in lines:
        ts = parse_ts(line)
        if ts is not None:
            if first_ts is None:
                first_ts = ts
            last_ts = ts
        m = COST_RE.search(line)
        if m:
            total_cost += float(m.group(1))
            n_cost_lines += 1

    if n_cost_lines == 0 or first_ts is None or last_ts is None:
        return None  # true error: nothing to mine

    latency = (last_ts - first_ts).total_seconds()
    return total_cost, latency


def main():
    for length, cases in [(1, L1_CASES), (4, L4_CASES), (9, L9_CASES)]:
        costs, latencies, excluded = [], [], []
        for c in cases:
            r = mine_case(length, c)
            if r is None:
                excluded.append(c)
                continue
            cost, latency = r
            costs.append(cost)
            latencies.append(latency)
        n = len(cases)
        print(f"\nL{length}: {len(costs)}/{n} cases with minable cost/latency data "
              f"(excluded true errors: {excluded})")
        if costs:
            print(f"  avg cost    = ${sum(costs)/len(costs):.4f}  "
                  f"(min=${min(costs):.4f}, max=${max(costs):.4f})")
            print(f"  avg latency = {sum(latencies)/len(latencies):.1f}s  "
                  f"(min={min(latencies):.1f}s, max={max(latencies):.1f}s)")

    # Overall across all 110
    all_costs, all_lat = [], []
    for length, cases in [(1, L1_CASES), (4, L4_CASES), (9, L9_CASES)]:
        for c in cases:
            r = mine_case(length, c)
            if r:
                all_costs.append(r[0])
                all_lat.append(r[1])
    print(f"\nOVERALL ({len(all_costs)}/110 minable):")
    print(f"  avg cost    = ${sum(all_costs)/len(all_costs):.4f}")
    print(f"  avg latency = {sum(all_lat)/len(all_lat):.1f}s")


if __name__ == "__main__":
    main()
