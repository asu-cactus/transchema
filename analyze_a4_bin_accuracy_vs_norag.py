"""
a4 simulate RAG miss-rate bins, with BOTH a4 (RAG) correctness and no-RAG correctness.
Bins are defined by the a4 per-case simulate miss-rate (from a4 logs).
For each bin: cases, a4 correct / %, no-RAG correct / % (over the same cases).
"""
import csv
import glob
import os
import re
from collections import defaultdict

RES = "/home/asurite.ad.asu.edu/jrtandel/transchema/Langraph/results_langraph"
A4_RES_GLOB = RES + "/mcts_l*_p*_rag_ub_partial_a4_pipeline_*/results_summary.csv"
NORAG_DIRS = [
    "mcts_pipeline_sim_len1_20260514_180950",
    "mcts_pipeline_sim_len4_20260514_190035",
    "mcts_pipeline_sim_len9_20260514_213349",
    "mcts_pipeline_len2356_len2_20260517_005542",
    "mcts_pipeline_len2356_len3_20260517_005542",
    "mcts_pipeline_len2356_len5_20260517_005542",
    "mcts_pipeline_len2356_len5_20260517_134131",
    "mcts_pipeline_len2356_len6_20260517_005542",
    "mcts_pipeline_len2356_len6_20260517_134131",
]
LOG_GLOB = "/home/asurite.ad.asu.edu/jrtandel/transchema/logs_langraph/mcts_l*_p*_rag_ub_partial_a4_pipeline/*.log"
ITER_RE = re.compile(r"\[simulate\] Iter \d+: mode=\w+, history=(\[.*\])\s*$")
HIT_RE = re.compile(r"\[simulate/pipeline\] RAG hints retrieved for prefix depth=(\d+)")
FNAME_RE = re.compile(r"(\d+)_target(\d+)_MCTS")


def load_correct(paths):
    d = {}
    for p in paths:
        if not os.path.exists(p):
            continue
        with open(p) as f:
            for row in csv.DictReader(f):
                d[row["case_id"]] = row["is_correct"].strip().lower() == "true"
    return d


a4_correct = load_correct(glob.glob(A4_RES_GLOB))
norag_correct = load_correct([f"{RES}/{d}/results_summary.csv" for d in NORAG_DIRS])
print(f"[info] a4 cases={len(a4_correct)} correct={sum(a4_correct.values())}")
print(f"[info] no-RAG cases={len(norag_correct)} correct={sum(norag_correct.values())}")

# ── a4 miss-rate per case ─────────────────────────────────────────────────────
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
B = range(10)
bin_cases = [0] * 10
bin_a4 = [0] * 10
bin_nr_cases = [0] * 10      # cases in bin that also have a no-RAG result
bin_nr = [0] * 10

for cid, is_c in a4_correct.items():
    tot = calls.get(cid, 0)
    if tot == 0:
        continue
    mr = (tot - hits.get(cid, 0)) / tot * 100
    b = 9 if mr >= 100 else int(mr // 10)
    bin_cases[b] += 1
    if is_c:
        bin_a4[b] += 1
    if cid in norag_correct:
        bin_nr_cases[b] += 1
        if norag_correct[cid]:
            bin_nr[b] += 1

print("\n" + "=" * 88)
print("a4 accuracy vs NO-RAG accuracy, by a4 simulate miss-rate bin")
print("=" * 88)
print(f"{'miss-rate bin':<14}{'cases':>7}{'a4 corr':>9}{'a4 %':>8}"
      f"{'noRAG n':>9}{'noRAG corr':>12}{'noRAG %':>9}{'Δ pts':>8}")
print("-" * 88)
for i in B:
    lo, hi = i * 10, i * 10 + 10
    t, a = bin_cases[i], bin_a4[i]
    nt, nr = bin_nr_cases[i], bin_nr[i]
    a4p = a / t * 100 if t else 0
    # no-RAG % computed over the SAME cases that have a no-RAG result
    nrp = nr / nt * 100 if nt else 0
    # comparable a4 % over the no-RAG-covered subset for a fair delta
    a4_on_nr = sum(1 for cid, c in a4_correct.items()
                   if cid in norag_correct and c and calls.get(cid, 0) > 0 and
                   (9 if (calls[cid]-hits.get(cid,0))/calls[cid]*100 >= 100
                    else int((calls[cid]-hits.get(cid,0))/calls[cid]*100//10)) == i)
    a4p_nr = a4_on_nr / nt * 100 if nt else 0
    dlt = f"{a4p_nr - nrp:+.1f}" if nt else "—"
    print(f"{f'{lo:>3}-{hi:>3}%':<14}{t:>7}{a:>9}{a4p:>7.1f}%"
          f"{nt:>9}{nr:>12}{nrp:>8.1f}%{dlt:>8}")
print("-" * 88)
T, A = sum(bin_cases), sum(bin_a4)
NT, NR = sum(bin_nr_cases), sum(bin_nr)
a4_on_nr_all = sum(1 for cid, c in a4_correct.items()
                   if cid in norag_correct and c and calls.get(cid, 0) > 0)
print(f"{'ALL':<14}{T:>7}{A:>9}{A/T*100:>7.1f}%"
      f"{NT:>9}{NR:>12}{NR/NT*100:>8.1f}%{a4_on_nr_all/NT*100 - NR/NT*100:>+7.1f}")
print(f"\nNote: 'Δ pts' compares a4 vs no-RAG on the SAME no-RAG-covered cases in each bin.")
print(f"      ({NT}/{T} binned cases have a matching no-RAG result.)")

with open("a4_bin_accuracy_vs_norag.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["miss_rate_bin", "cases", "a4_correct", "a4_pct",
                "norag_cases", "norag_correct", "norag_pct"])
    for i in B:
        t, a, nt, nr = bin_cases[i], bin_a4[i], bin_nr_cases[i], bin_nr[i]
        w.writerow([f"{i*10}-{i*10+10}%", t, a, f"{(a/t*100 if t else 0):.1f}",
                    nt, nr, f"{(nr/nt*100 if nt else 0):.1f}"])
print("Wrote: a4_bin_accuracy_vs_norag.csv")
