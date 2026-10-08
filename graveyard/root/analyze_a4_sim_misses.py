"""
Analyze WHY a4 (upper_bound) simulation RAG hit-rate is low, even though every
case has exactly one matching pipeline (its own ground truth) in the local DB.

A pipeline-simulate RAG hit happens iff:
    gt_abstract[:depth] == sim_abstract_prefix  AND  len(gt_abstract) > depth

So every call is exactly one of:
  HIT
  MISS-divergent    : sim path is NOT a prefix of the GT path (MCTS explored a
                      different branch, or operator order/granularity differs)
  MISS-exhausted    : sim path == GT prefix, but depth >= len(GT) — rollout has
                      already reached/passed full GT length; the single GT entry
                      has no "next step" left to offer
  MISS-no_struct_gt : GT has no structural operators (all dropped) -> DB entry's
                      abstract pipeline is empty, can never match.
"""
import ast
import csv
import glob
import os
import re
from collections import defaultdict

GT_CSV = "/home/asurite.ad.asu.edu/jrtandel/transchema/ground_truth_pipelines.csv"
LOG_GLOB = "/home/asurite.ad.asu.edu/jrtandel/transchema/logs_langraph/mcts_l*_p*_rag_ub_partial_a4_pipeline/*.log"

_OP_TO_BIN = {
    "JOIN": "merge", "UNION": "union", "GROUP_BY/AGGREGATE": "groupby",
    "PIVOT": "pivot", "UNPIVOT": "unpivot", "NO_MORE_OPERATION": "terminal",
}
GT_OP_TO_MCTS = {
    "merge": "JOIN", "groupby": "GROUP_BY/AGGREGATE", "concat": "UNION",
    "union": "UNION", "pivot": "PIVOT", "unpivot": "UNPIVOT",
}


def step_to_abstract(step):
    return _OP_TO_BIN.get(step.split(":")[0].strip().upper(), "other")


def gt_abstract_for(ops):
    steps = [GT_OP_TO_MCTS[o.strip().lower()] for o in ops if o.strip().lower() in GT_OP_TO_MCTS]
    if steps:
        steps.append("NO_MORE_OPERATION")
    return [step_to_abstract(s) for s in steps]


def classify(depth, sim_prefix, gta):
    """Return one of: hit, divergent, exhausted, no_struct_gt."""
    if not gta:
        return "no_struct_gt"
    if gta[:depth] == sim_prefix:
        return "hit" if len(gta) > depth else "exhausted"
    return "divergent"


# ── Load GT abstract pipelines keyed by case id "L_idx" ───────────────────────
gt = {}
with open(GT_CSV, encoding="latin-1") as f:
    for row in csv.DictReader(f):
        m = re.match(r"Target(\d+)_(\d+)", row["target_id"])
        if not m:
            continue
        gt[f"{m.group(1)}_{m.group(2)}"] = gt_abstract_for(ast.literal_eval(row["operators"]))

ITER_RE = re.compile(r"\[simulate\] Iter \d+: mode=\w+, history=(\[.*\])\s*$")
HIT_RE = re.compile(r"\[simulate/pipeline\] RAG hints retrieved for prefix depth=(\d+)")
FNAME_RE = re.compile(r"(\d+)_target(\d+)_MCTS")

per_len = defaultdict(lambda: defaultdict(int))   # length -> bucket -> count
d1 = defaultdict(lambda: [0, 0])                   # length -> [depth1_total, depth1_hit]
div_deeper = defaultdict(int)                      # length -> divergent where sim deeper than GT
div_other = defaultdict(int)                       # length -> divergent involving an 'other' bin


def record(length, depth, sim_prefix, gta):
    bucket = classify(depth, sim_prefix, gta)
    per_len[length][bucket] += 1
    per_len[length]["total"] += 1
    if depth == 1:
        d1[length][0] += 1
        if bucket == "hit":
            d1[length][1] += 1
    if bucket == "divergent":
        if gta and depth > len(gta):
            div_deeper[length] += 1
        if "other" in sim_prefix:
            div_other[length] += 1


for path in glob.glob(LOG_GLOB):
    fm = FNAME_RE.match(os.path.basename(path))
    if not fm:
        continue
    length = int(fm.group(1))
    gta = gt.get(f"{fm.group(1)}_{fm.group(2)}")
    pending = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            im = ITER_RE.search(line)
            if im:
                if pending is not None:
                    record(length, pending[0], pending[1], gta)
                try:
                    hist = ast.literal_eval(im.group(1))
                except Exception:
                    hist = []
                sp = [step_to_abstract(s) for s in hist]
                pending = (len(sp), sp)
                continue
            if HIT_RE.search(line) and pending is not None:
                # mark as resolved-hit by overwriting bucket logic: force hit
                per_len[length]["hit"] += 1
                per_len[length]["total"] += 1
                if pending[0] == 1:
                    d1[length][0] += 1
                    d1[length][1] += 1
                pending = None
        if pending is not None:
            record(length, pending[0], pending[1], gta)

# ── Report ────────────────────────────────────────────────────────────────────
lengths = sorted(per_len)
buckets = ["hit", "divergent", "exhausted", "no_struct_gt"]

print("=" * 92)
print("a4 (upper_bound) — pipeline-simulate RAG outcome decomposition")
print("=" * 92)
hdr = f"{'Len':<5}{'Total':>8}{'HIT':>8}{'HIT%':>7}{'diverg':>9}{'exhaust':>9}{'noGTops':>9}"
print(hdr)
print("-" * 92)
tot = defaultdict(int)
for L in lengths:
    c = per_len[L]
    t = c["total"]
    for b in buckets:
        tot[b] += c[b]
    tot["total"] += t
    print(f"{('L'+str(L)):<5}{t:>8}{c['hit']:>8}{(c['hit']/t*100 if t else 0):>6.1f}%"
          f"{c['divergent']:>9}{c['exhausted']:>9}{c['no_struct_gt']:>9}")
print("-" * 92)
t = tot["total"]
print(f"{'ALL':<5}{t:>8}{tot['hit']:>8}{(tot['hit']/t*100):>6.1f}%"
      f"{tot['divergent']:>9}{tot['exhausted']:>9}{tot['no_struct_gt']:>9}")
print()
print("Share of all MISSES by reason:")
miss = t - tot["hit"]
for b in ["divergent", "exhausted", "no_struct_gt"]:
    print(f"  {b:<14}: {tot[b]:>6}  ({tot[b]/miss*100:5.1f}% of misses)")
print()
print("Depth-1 (first simulated op) hit rate = 'did MCTS pick the right FIRST operator':")
d1t = sum(d1[L][0] for L in lengths)
d1h = sum(d1[L][1] for L in lengths)
for L in lengths:
    tt, hh = d1[L]
    print(f"  L{L}: {hh}/{tt} = {(hh/tt*100 if tt else 0):.1f}%")
print(f"  ALL: {d1h}/{d1t} = {(d1h/d1t*100 if d1t else 0):.1f}%")
print()
print("Of divergent misses:")
print(f"  involve an 'other' (unbinnable) op in sim path : {sum(div_other.values())}")
print(f"  sim explored DEEPER than the full GT length     : {sum(div_deeper.values())}")
