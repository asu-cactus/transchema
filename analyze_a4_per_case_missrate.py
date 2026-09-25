"""
Is the a4 simulate RAG miss-rate case-specific?

Per case: miss_rate = (sim calls with NO RAG hint) / (total sim calls).
Bin cases into deciles of miss-rate and print a histogram + write a per-case CSV.
"""
import ast
import glob
import os
import re
from collections import defaultdict

LOG_GLOB = "/home/asurite.ad.asu.edu/jrtandel/transchema/logs_langraph/mcts_l*_p*_rag_ub_partial_a4_pipeline/*.log"
ITER_RE = re.compile(r"\[simulate\] Iter \d+: mode=\w+, history=(\[.*\])\s*$")
HIT_RE = re.compile(r"\[simulate/pipeline\] RAG hints retrieved for prefix depth=(\d+)")
FNAME_RE = re.compile(r"(\d+)_target(\d+)_MCTS")

# case_id -> [total_calls, hits]
case = defaultdict(lambda: [0, 0])

for path in glob.glob(LOG_GLOB):
    fm = FNAME_RE.match(os.path.basename(path))
    if not fm:
        continue
    case_id = f"{fm.group(1)}_{fm.group(2)}"
    pending = False
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if ITER_RE.search(line):
                case[case_id][0] += 1
                pending = True
            elif HIT_RE.search(line) and pending:
                case[case_id][1] += 1
                pending = False

rows = []
for cid, (tot, hit) in case.items():
    if tot == 0:
        continue
    miss_rate = (tot - hit) / tot * 100
    rows.append((cid, tot, hit, tot - hit, miss_rate))

# ── Histogram of miss-rate ────────────────────────────────────────────────────
bins = [0] * 10                  # [0-10), [10-20), ... [90-100]
bin100 = 0                       # exactly 100%
bin0 = 0                         # exactly 0%
for _, _, _, _, mr in rows:
    if mr >= 100:
        bins[9] += 1
        bin100 += 1
    else:
        bins[int(mr // 10)] += 1
    if mr == 0:
        bin0 += 1

n = len(rows)
print(f"Total cases (a4): {n}")
print(f"Mean per-case miss-rate: {sum(r[4] for r in rows)/n:.1f}%")
print()
print("Histogram — # of cases by % of simulate calls that MISSED RAG")
print("-" * 60)
labels = [f"{i*10:>3}-{i*10+10:>3}%" for i in range(10)]
mx = max(bins) or 1
for i in range(10):
    bar = "█" * round(bins[i] / mx * 34)
    print(f"  {labels[i]} | {bins[i]:>4}  {bar}")
print("-" * 60)
print(f"  (of the top bin, {bin100} cases are EXACTLY 100% miss — RAG never hit)")
print(f"  ({bin0} cases are EXACTLY 0% miss — RAG hit on every simulate call)")

# ── Per-case CSV ──────────────────────────────────────────────────────────────
import csv
rows.sort(key=lambda r: -r[4])
with open("a4_per_case_miss_rate.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["case_id", "length", "sim_calls", "hits", "misses", "miss_rate_pct"])
    for cid, tot, hit, miss, mr in rows:
        w.writerow([cid, cid.split("_")[0], tot, hit, miss, f"{mr:.1f}"])
print("\nWrote: a4_per_case_miss_rate.csv (sorted worst-first)")

# concentration: what share of all misses come from the worst quartile of cases?
total_miss = sum(r[3] for r in rows)
rows_by_miss = sorted(rows, key=lambda r: -r[3])
q = max(1, n // 4)
top_q_miss = sum(r[3] for r in rows_by_miss[:q])
print(f"\nConcentration: the worst {q} cases ({q/n*100:.0f}% of cases) account for "
      f"{top_q_miss}/{total_miss} = {top_q_miss/total_miss*100:.0f}% of all misses.")
