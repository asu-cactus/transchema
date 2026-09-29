"""
Global RAG: why does pipeline-simulate rarely find a prefix match among the 50
schema-similar examples, and what happens to the hit rate at top-100?

Method (faithful replay):
  1. For every case that ran in the global experiment, load its target+source
     schema exactly as mcts_search does (get_test_info) and re-run the global
     schema-embedding search for top-100 candidates.
  2. Convert each candidate's pipeline text to abstract operator bins (identical
     to local_rag_db.populate_from_global_results -> step_to_abstract).
  3. Replay the case's ACTUAL simulate histories (parsed from the global logs)
     against the top-50 and top-100 candidate sets.  A call is a HIT iff some
     candidate has  abstract[:depth] == sim_prefix  AND  len(abstract) > depth.
  4. Report hit rate @50 (should reproduce the observed ~19.3%) vs @100, plus a
     diagnosis of why the 50 miss.
"""
import ast
import csv
import glob
import json
import os
import re
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "/home/asurite.ad.asu.edu/jrtandel/transchema")
from rag_pipeline.global_rag_db import GlobalSchemaDB, format_schema_text
from util.utils import get_test_info

MAIN_FOLDER = "autopipeline-benchmarks/github-pipelines"
DB = "rag_pipeline/db/global_schema"
LOG_GLOB = "/home/asurite.ad.asu.edu/jrtandel/transchema/logs_langraph/mcts_l*_p*_rag_global_partial_pipeline/*.log"

_OP_TO_BIN = {
    "JOIN": "merge", "UNION": "union", "GROUP_BY/AGGREGATE": "groupby",
    "PIVOT": "pivot", "UNPIVOT": "unpivot", "NO_MORE_OPERATION": "terminal",
}


def step_to_abstract(step):
    return _OP_TO_BIN.get(step.split(":")[0].strip().upper(), "other")


def pipeline_to_abstract(pipeline_text):
    steps = [ln.strip() for ln in pipeline_text.splitlines() if ln.strip()]
    return tuple(step_to_abstract(s) for s in steps)


ITER_RE = re.compile(r"\[simulate\] Iter \d+: mode=\w+, history=(\[.*\])\s*$")
FNAME_RE = re.compile(r"(\d+)_target(\d+)_MCTS")

# ── 1. Collect cases + their simulate histories from the global logs ──────────
case_histories = defaultdict(list)   # "L_idx" -> list of sim_prefix tuples
for path in glob.glob(LOG_GLOB):
    fm = FNAME_RE.match(os.path.basename(path))
    if not fm:
        continue
    case_id = f"{fm.group(1)}_{fm.group(2)}"
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            im = ITER_RE.search(line)
            if im:
                try:
                    hist = ast.literal_eval(im.group(1))
                except Exception:
                    hist = []
                case_histories[case_id].append(tuple(step_to_abstract(s) for s in hist))

cases = sorted(case_histories, key=lambda c: (int(c.split("_")[0]), int(c.split("_")[1])))
print(f"[info] {len(cases)} cases, "
      f"{sum(len(v) for v in case_histories.values())} simulate calls total")

# ── 2. Load schemas + build query text for each case ──────────────────────────
gdb = GlobalSchemaDB(DB)               # loads embeddings + records (read-only)
records = gdb._records
emb = gdb._embeddings                  # (N, dim), L2-normalised

# Precompute abstract pipeline for every global record once.
rec_abstract = [pipeline_to_abstract(r.get("pipeline", "")) for r in records]

query_texts, valid_cases = [], []
for case_id in cases:
    length = case_id.split("_")[0]
    file_count = 1
    json_file = ("data/chatgpt_github_ms.json"
                 if os.path.isdir(f"{MAIN_FOLDER}/length{case_id}") and
                 sum(1 for f in os.listdir(f"{MAIN_FOLDER}/length{case_id}")
                     if f.startswith("test") and
                     os.path.isfile(os.path.join(f"{MAIN_FOLDER}/length{case_id}", f))) > 1
                 else "data/chatgpt_github_ss.json")
    try:
        (_tname, tschema, _twt, _ts, _fc, _snames, sschemas, _ss) = get_test_info(
            json_file, case_id, MAIN_FOLDER, 0, data_split="test")
    except Exception as e:
        print(f"[warn] {case_id}: get_test_info failed ({e}) — skipped")
        continue
    if tschema is None:
        print(f"[warn] {case_id}: no schema — skipped")
        continue
    query_texts.append(format_schema_text(tschema, sschemas))
    valid_cases.append(case_id)

# ── 3. Batch-embed all queries, one matmul per case for top-k ─────────────────
print(f"[info] embedding {len(query_texts)} case queries ...")
embedder = gdb._get_embedder()
qmat = embedder.encode(query_texts, batch_size=64)     # (C, dim)

TOPN = 100
case_topk = {}     # case_id -> list of abstract-pipeline tuples (top 100, ranked)
for ci, case_id in enumerate(valid_cases):
    sims = emb @ qmat[ci]
    idx = np.argpartition(sims, -TOPN)[-TOPN:]
    idx = idx[np.argsort(sims[idx])[::-1]]
    case_topk[case_id] = [rec_abstract[int(j)] for j in idx]

# ── 3b. Pool operator-diversity: does sending 100 add genuinely NEW shapes? ───
fmt = lambda seq: ">".join(seq) if seq else "(empty)"
pool_shape_freq = defaultdict(int)        # abstract shape -> count across all top-50 pools
pool_shape_cases = defaultdict(set)       # abstract shape -> set of cases it appears in
div_by_len = defaultdict(lambda: {"n": 0, "d50": 0, "d100": 0, "new": 0, "domshare": 0.0})
for case_id in valid_cases:
    L = int(case_id.split("_")[0])
    top100 = case_topk[case_id]
    top50 = top100[:50]
    s50, s100 = set(top50), set(top100)
    cnt = defaultdict(int)
    for ab in top50:
        cnt[ab] += 1
        pool_shape_freq[ab] += 1
    for ab in s50:
        pool_shape_cases[ab].add(case_id)
    dom = max(cnt.values()) / len(top50) if top50 else 0
    d = div_by_len[L]
    d["n"] += 1
    d["d50"] += len(s50)
    d["d100"] += len(s100)
    d["new"] += len(s100 - s50)
    d["domshare"] += dom

# ── 4. Replay histories against top-50 and top-100 ────────────────────────────
def has_prefix_match(cand_set, sim_prefix):
    depth = len(sim_prefix)
    sp = tuple(sim_prefix)
    for ab in cand_set:
        if len(ab) > depth and ab[:depth] == sp:
            return True
    return False


per_len = defaultdict(lambda: {"calls": 0, "hit50": 0, "hit100": 0,
                               "first_op_absent": 0, "depth": 0})
# Decompose misses@50: d1_firstop_absent / deep_firstop_absent / deep_seq_absent
miss_kind = defaultdict(int)
for case_id in valid_cases:
    L = int(case_id.split("_")[0])
    top100 = case_topk[case_id]
    top50 = top100[:50]
    first_ops_50 = {ab[0] for ab in top50 if ab}   # first-op bins available in the 50
    for sp in case_histories[case_id]:
        d = per_len[L]
        d["calls"] += 1
        d["depth"] += len(sp)
        h50 = has_prefix_match(top50, sp)
        h100 = has_prefix_match(top100, sp)
        if h50:
            d["hit50"] += 1
        if h100:
            d["hit100"] += 1
        first_absent = len(sp) >= 1 and sp[0] not in first_ops_50
        if not h50:
            if first_absent:
                d["first_op_absent"] += 1
            if len(sp) <= 1:
                miss_kind["d1_no_first_op" if first_absent else "d1_other"] += 1
            else:
                miss_kind["deep_no_first_op" if first_absent
                          else "deep_seq_absent"] += 1

# ── 5. Report ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 96)
print("Global RAG — pipeline-simulate prefix-match hit rate @50 vs @100 (faithful replay)")
print("=" * 96)
print(f"{'Len':<5}{'calls':>8}{'hit@50':>9}{'%@50':>8}{'hit@100':>9}{'%@100':>8}"
      f"{'Δ pts':>8}{'1stOpAbs':>10}")
print("-" * 96)
tot = defaultdict(int)
for L in sorted(per_len):
    d = per_len[L]
    c = d["calls"]
    p50 = d["hit50"] / c * 100
    p100 = d["hit100"] / c * 100
    for k in ("calls", "hit50", "hit100", "first_op_absent"):
        tot[k] += d[k]
    print(f"{('L'+str(L)):<5}{c:>8}{d['hit50']:>9}{p50:>7.1f}%{d['hit100']:>9}"
          f"{p100:>7.1f}%{p100-p50:>+7.1f}{d['first_op_absent']:>10}")
print("-" * 96)
c = tot["calls"]
print(f"{'ALL':<5}{c:>8}{tot['hit50']:>9}{tot['hit50']/c*100:>7.1f}%{tot['hit100']:>9}"
      f"{tot['hit100']/c*100:>7.1f}%{(tot['hit100']-tot['hit50'])/c*100:>+7.1f}"
      f"{tot['first_op_absent']:>10}")
print()
print(f"Observed (from grep) simulate hits @50 = 871 / {c} = {871/c*100:.1f}%  "
      f"(replay@50 = {tot['hit50']} → validates method)")
miss50 = c - tot["hit50"]
print(f"Decomposition of the {miss50} misses@50:")
mk = miss_kind
order = [
    ("d1_no_first_op", "depth-1 rollout, first op absent from the 50"),
    ("d1_other",       "depth-1 rollout, first op present but no longer pipeline (rare)"),
    ("deep_no_first_op", "depth>=2 rollout, first op already absent from the 50"),
    ("deep_seq_absent",  "depth>=2 rollout, first op present BUT the full sequence absent"),
]
for k, label in order:
    if mk[k]:
        print(f"  {mk[k]:>6} ({mk[k]/miss50*100:4.1f}%)  {label}")

# ── 6. Pool diversity report + CSVs ───────────────────────────────────────────
print("\n" + "=" * 96)
print("Pool operator-diversity — why 50→100 adds little: are the extra pipelines just more")
print("of the same operator shapes?")
print("=" * 96)
print(f"{'Len':<5}{'cases':>7}{'distinct@50':>13}{'distinct@100':>14}{'NEW@100':>9}"
      f"{'dom-shape%@50':>15}")
print("-" * 96)
T = defaultdict(float)
for L in sorted(div_by_len):
    d = div_by_len[L]
    n = d["n"]
    for k in ("n", "d50", "d100", "new"):
        T[k] += d[k]
    T["domshare"] += d["domshare"]
    print(f"{('L'+str(L)):<5}{n:>7}{d['d50']/n:>13.1f}{d['d100']/n:>14.1f}"
          f"{d['new']/n:>9.1f}{d['domshare']/n*100:>14.1f}%")
print("-" * 96)
n = T["n"]
print(f"{'ALL':<5}{int(n):>7}{T['d50']/n:>13.1f}{T['d100']/n:>14.1f}{T['new']/n:>9.1f}"
      f"{T['domshare']/n*100:>14.1f}%")
print()
print(f"On average a top-50 pool contains only {T['d50']/n:.1f} DISTINCT operator shapes "
      f"out of 50 pipelines.")
print(f"Going to top-100 adds just {T['new']/n:.1f} new distinct shapes — the extra 50 are "
      f"mostly duplicates")
print(f"of shapes already present.  The single most common shape already fills "
      f"{T['domshare']/n*100:.0f}% of the pool.")

with open("global_pool_diversity_by_len.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["length", "cases", "avg_distinct_shapes_top50",
                "avg_distinct_shapes_top100", "avg_new_shapes_at_100",
                "avg_dominant_shape_share_top50"])
    for L in sorted(div_by_len):
        d = div_by_len[L]
        n = d["n"]
        w.writerow([L, n, f"{d['d50']/n:.2f}", f"{d['d100']/n:.2f}",
                    f"{d['new']/n:.2f}", f"{d['domshare']/n:.3f}"])

with open("global_pool_shape_frequency.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["abstract_shape", "total_occurrences_across_top50_pools",
                "num_cases_present"])
    for ab, c in sorted(pool_shape_freq.items(), key=lambda x: -x[1]):
        w.writerow([fmt(ab), c, len(pool_shape_cases[ab])])

miss_seq = defaultdict(int)
for case_id in valid_cases:
    top50 = case_topk[case_id][:50]
    for sp in case_histories[case_id]:
        if not has_prefix_match(top50, sp):
            miss_seq[(fmt(sp), len(sp))] += 1
with open("global_missing_sequence_patterns.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rollout_sequence", "depth", "frequency"])
    for (s, d), c in sorted(miss_seq.items(), key=lambda x: -x[1]):
        w.writerow([s, d, c])

print("\nTOP 15 global pool shapes (what kind of pipelines schema-similarity keeps pulling in)")
print("-" * 84)
print(f"{'abstract_shape':<46}{'occurrences':>13}{'cases':>8}")
for ab, c in sorted(pool_shape_freq.items(), key=lambda x: -x[1])[:15]:
    print(f"{fmt(ab)[:44]:<46}{c:>13}{len(pool_shape_cases[ab]):>8}")
print("\nWrote: global_pool_diversity_by_len.csv, global_pool_shape_frequency.csv, "
      "global_missing_sequence_patterns.csv")
