"""
Extend the a4 miss-rate bins with GLOBAL-experiment numbers, over the SAME cases
(bins are defined by a4 simulate miss-rate).

Per bin: cases, a4 %, no-RAG %, global %, avg a4 RAG hits/case, avg global RAG hits/case.
"""
import csv
import glob
import os
import re
from collections import defaultdict

RES = "/home/asurite.ad.asu.edu/jrtandel/transchema/Langraph/results_langraph"
A4_RES = RES + "/mcts_l*_p*_rag_ub_partial_a4_pipeline_*/results_summary.csv"
GL_RES = RES + "/mcts_l*_p*_rag_global_partial_pipeline_*/results_summary.csv"
NORAG_DIRS = [
    "mcts_pipeline_sim_len1_20260514_180950", "mcts_pipeline_sim_len4_20260514_190035",
    "mcts_pipeline_sim_len9_20260514_213349", "mcts_pipeline_len2356_len2_20260517_005542",
    "mcts_pipeline_len2356_len3_20260517_005542", "mcts_pipeline_len2356_len5_20260517_005542",
    "mcts_pipeline_len2356_len5_20260517_134131", "mcts_pipeline_len2356_len6_20260517_005542",
    "mcts_pipeline_len2356_len6_20260517_134131",
]
A4_LOG = "/home/asurite.ad.asu.edu/jrtandel/transchema/logs_langraph/mcts_l*_p*_rag_ub_partial_a4_pipeline/*.log"
GL_LOG = "/home/asurite.ad.asu.edu/jrtandel/transchema/logs_langraph/mcts_l*_p*_rag_global_partial_pipeline/*.log"
ITER_RE = re.compile(r"\[simulate\] Iter \d+: mode=\w+, history=(\[.*\])\s*$")
HIT_RE = re.compile(r"\[simulate/pipeline\] RAG hints retrieved for prefix depth=(\d+)")
FNAME_RE = re.compile(r"(\d+)_target(\d+)_MCTS")


def load_correct(paths):
    d = {}
    for p in paths:
        if os.path.exists(p):
            with open(p) as f:
                for row in csv.DictReader(f):
                    d[row["case_id"]] = row["is_correct"].strip().lower() == "true"
    return d


def parse_hits(log_glob):
    calls, hits = defaultdict(int), defaultdict(int)
    for path in glob.glob(log_glob):
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
    return calls, hits


a4_correct = load_correct(glob.glob(A4_RES))
gl_correct = load_correct(glob.glob(GL_RES))
nr_correct = load_correct([f"{RES}/{d}/results_summary.csv" for d in NORAG_DIRS])
a4_calls, a4_hits = parse_hits(A4_LOG)
gl_calls, gl_hits = parse_hits(GL_LOG)
print(f"[info] a4 correct={sum(a4_correct.values())}/{len(a4_correct)}  "
      f"global correct={sum(gl_correct.values())}/{len(gl_correct)}  "
      f"noRAG correct={sum(nr_correct.values())}/{len(nr_correct)}")

# ── bin by a4 miss-rate ───────────────────────────────────────────────────────
n = 10
cases = [0]*n
a4c = [0]*n
glc = [0]*n; gl_n = [0]*n               # global correct + #cases covered by global
a4_hit = [0]*n; a4_call = [0]*n         # aggregate hits / calls (a4) over bin cases
gl_hit = [0]*n; gl_call = [0]*n         # aggregate hits / calls (global) over bin cases

for cid, isc in a4_correct.items():
    tot = a4_calls.get(cid, 0)
    if tot == 0:
        continue
    mr = (tot - a4_hits.get(cid, 0)) / tot * 100
    b = 9 if mr >= 100 else int(mr // 10)
    cases[b] += 1
    a4c[b] += int(isc)
    a4_hit[b] += a4_hits.get(cid, 0)
    a4_call[b] += tot
    if cid in gl_correct:
        gl_n[b] += 1
        glc[b] += int(gl_correct[cid])
    if cid in gl_calls:
        gl_hit[b] += gl_hits.get(cid, 0)
        gl_call[b] += gl_calls.get(cid, 0)

print("\n" + "=" * 96)
print("a4 miss-rate bins — accuracy (a4 / global) + simulate RAG hit-rate (% of sim calls)")
print("=" * 96)
print(f"{'bin':<11}{'cases':>6}{'a4 acc%':>9}{'glob acc%':>11}"
      f"{'a4 RAG hit%':>14}{'glob RAG hit%':>16}")
print("-" * 96)
for i in range(n):
    lo, hi = i*10, i*10+10
    c = cases[i]
    a4p = a4c[i]/c*100 if c else 0
    glp = glc[i]/gl_n[i]*100 if gl_n[i] else 0
    a4hr = a4_hit[i]/a4_call[i]*100 if a4_call[i] else 0
    glhr = gl_hit[i]/gl_call[i]*100 if gl_call[i] else 0
    print(f"{f'{lo:>3}-{hi:>3}%':<11}{c:>6}{a4p:>8.1f}%{glp:>10.1f}%"
          f"{a4hr:>13.1f}%{glhr:>15.1f}%")
print("-" * 96)
C = sum(cases)
A4HR = sum(a4_hit)/sum(a4_call)*100
GLHR = sum(gl_hit)/sum(gl_call)*100
print(f"{'ALL':<11}{C:>6}{sum(a4c)/C*100:>8.1f}%{sum(glc)/sum(gl_n)*100:>10.1f}%"
      f"{A4HR:>13.1f}%{GLHR:>15.1f}%")
print("\nNotes:")
print("  - bins defined by a4 simulate miss-rate.")
print("  - RAG hit% = (sum simulate RAG hits) / (sum simulate calls) across the bin's cases.")

with open("a4_bin_global_compare.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["miss_rate_bin", "cases", "a4_acc_pct", "global_acc_pct",
                "a4_rag_hit_pct", "global_rag_hit_pct"])
    for i in range(n):
        c = cases[i]
        a4hr = a4_hit[i]/a4_call[i]*100 if a4_call[i] else 0
        glhr = gl_hit[i]/gl_call[i]*100 if gl_call[i] else 0
        w.writerow([f"{i*10}-{i*10+10}%", c,
                    f"{(a4c[i]/c*100 if c else 0):.1f}",
                    f"{(glc[i]/gl_n[i]*100 if gl_n[i] else 0):.1f}",
                    f"{a4hr:.1f}", f"{glhr:.1f}"])
print("Wrote: a4_bin_global_compare.csv")
