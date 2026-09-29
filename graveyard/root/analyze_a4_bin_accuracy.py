"""
a4: cross per-case simulate RAG miss-rate (deciles) with final correctness.
For each miss-rate bin: total cases, # correct, % correct.

miss-rate source: parsed from logs ([simulate] Iter vs RAG-hit lines).
correctness source: Langraph/results_langraph/<a4 experiment>/results_summary.csv
"""
import csv
import glob
import os
import re
from collections import defaultdict

RES_GLOB = "/home/asurite.ad.asu.edu/jrtandel/transchema/Langraph/results_langraph/mcts_l*_p*_rag_ub_partial_a4_pipeline_*/results_summary.csv"
LOG_GLOB = "/home/asurite.ad.asu.edu/jrtandel/transchema/logs_langraph/mcts_l*_p*_rag_ub_partial_a4_pipeline/*.log"
ITER_RE = re.compile(r"\[simulate\] Iter \d+: mode=\w+, history=(\[.*\])\s*$")
HIT_RE = re.compile(r"\[simulate/pipeline\] RAG hints retrieved for prefix depth=(\d+)")
FNAME_RE = re.compile(r"(\d+)_target(\d+)_MCTS")

# ── correctness per case ──────────────────────────────────────────────────────
correct = {}
for res in glob.glob(RES_GLOB):
    with open(res) as f:
        for row in csv.DictReader(f):
            correct[row["case_id"]] = row["is_correct"].strip().lower() == "true"
print(f"[info] {len(correct)} cases with correctness; "
      f"{sum(correct.values())} correct overall")

# ── miss-rate per case from logs ──────────────────────────────────────────────
calls = defaultdict(int)
hits = defaultdict(int)
for path in glob.glob(LOG_GLOB):
    fm = FNAME_RE.match(os.path.basename(path))
    if not fm:
        continue
    cid = f"{fm.group(1)}_{fm.group(2)}"
    pending = False
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if ITER_RE.search(line):
                calls[cid] += 1
                pending = True
            elif HIT_RE.search(line) and pending:
                hits[cid] += 1
                pending = False

# ── bin and tabulate ──────────────────────────────────────────────────────────
# bin index 0..9 for miss-rate [0,10),...,[90,100]
bin_total = [0] * 10
bin_correct = [0] * 10
no_simcall_cases = 0     # cases in results but with no simulate calls logged
for cid, is_c in correct.items():
    tot = calls.get(cid, 0)
    if tot == 0:
        no_simcall_cases += 1
        continue
    mr = (tot - hits.get(cid, 0)) / tot * 100
    b = 9 if mr >= 100 else int(mr // 10)
    bin_total[b] += 1
    if is_c:
        bin_correct[b] += 1

print("\n" + "=" * 64)
print("a4 — accuracy by simulate RAG miss-rate bin")
print("=" * 64)
print(f"{'miss-rate bin':<16}{'cases':>8}{'correct':>10}{'% correct':>12}")
print("-" * 64)
for i in range(10):
    lo, hi = i * 10, i * 10 + 10
    t, c = bin_total[i], bin_correct[i]
    pct = f"{c/t*100:.1f}%" if t else "—"
    print(f"{f'{lo:>3}-{hi:>3}%':<16}{t:>8}{c:>10}{pct:>12}")
print("-" * 64)
T, C = sum(bin_total), sum(bin_correct)
print(f"{'ALL (w/ sim)':<16}{T:>8}{C:>10}{C/T*100:>11.1f}%")
if no_simcall_cases:
    print(f"\n({no_simcall_cases} cases had no simulate calls logged — excluded above)")

# also coarse 2-camp view
lo_total = sum(bin_total[:1]); lo_corr = sum(bin_correct[:1])      # 0-10%
hi_total = sum(bin_total[9:]); hi_corr = sum(bin_correct[9:])      # 90-100%
mid_total = sum(bin_total[1:9]); mid_corr = sum(bin_correct[1:9])
print("\nTwo-camp summary:")
print(f"  near-always HIT (0-10% miss) : {lo_corr}/{lo_total} = {lo_corr/lo_total*100:.1f}% correct")
print(f"  middle (10-90% miss)         : {mid_corr}/{mid_total} = {mid_corr/mid_total*100:.1f}% correct")
print(f"  near-always MISS (90-100%)   : {hi_corr}/{hi_total} = {hi_corr/hi_total*100:.1f}% correct")

with open("a4_bin_accuracy.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["miss_rate_bin", "cases", "correct", "pct_correct"])
    for i in range(10):
        t, c = bin_total[i], bin_correct[i]
        w.writerow([f"{i*10}-{i*10+10}%", t, c, f"{(c/t*100 if t else 0):.1f}"])
print("\nWrote: a4_bin_accuracy.csv")
