"""
a4 divergence patterns: for every DIVERGENT simulate miss (rollout path is not a
prefix of the case's ground-truth path), record what pipeline the rollout was on
vs the GT shape.  Produces frequency-ordered CSVs so we can see which kinds of
pipelines cause the most prefix-match failures.

Outputs:
  a4_divergence_patterns.csv    [gt_pipeline, rollout_prefix, depth, frequency]
  a4_divergence_by_gt_shape.csv [gt_pipeline, divergent_misses, distinct_cases, hit_calls]
  a4_divergence_by_rollout.csv  [rollout_prefix, depth, frequency]
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
    return tuple(step_to_abstract(s) for s in steps)


gt = {}
with open(GT_CSV, encoding="latin-1") as f:
    for row in csv.DictReader(f):
        m = re.match(r"Target(\d+)_(\d+)", row["target_id"])
        if m:
            gt[f"{m.group(1)}_{m.group(2)}"] = gt_abstract_for(ast.literal_eval(row["operators"]))

ITER_RE = re.compile(r"\[simulate\] Iter \d+: mode=\w+, history=(\[.*\])\s*$")
HIT_RE = re.compile(r"\[simulate/pipeline\] RAG hints retrieved for prefix depth=(\d+)")
FNAME_RE = re.compile(r"(\d+)_target(\d+)_MCTS")

fmt = lambda seq: ">".join(seq) if seq else "(empty)"

pat = defaultdict(int)                      # (gt_str, rollout_str, depth) -> freq
by_gt = defaultdict(lambda: [0, set(), 0])  # gt_str -> [divergent_misses, cases, hit_calls]
by_rollout = defaultdict(int)               # (rollout_str, depth) -> freq


def resolve(length, case_id, depth, sim_prefix, gta, is_hit):
    gt_str = fmt(gta) if gta else "(no_struct_gt)"
    if is_hit:
        by_gt[gt_str][2] += 1
        return
    if gta and gta[:depth] == sim_prefix:    # exhausted, not a divergence
        return
    # divergent
    rstr = fmt(sim_prefix)
    pat[(gt_str, rstr, depth)] += 1
    by_gt[gt_str][0] += 1
    by_gt[gt_str][1].add(case_id)
    by_rollout[(rstr, depth)] += 1


for path in glob.glob(LOG_GLOB):
    fm = FNAME_RE.match(os.path.basename(path))
    if not fm:
        continue
    length = int(fm.group(1))
    case_id = f"{fm.group(1)}_{fm.group(2)}"
    gta = gt.get(case_id)
    pending = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            im = ITER_RE.search(line)
            if im:
                if pending is not None:
                    resolve(length, case_id, pending[0], pending[1], gta, False)
                try:
                    hist = ast.literal_eval(im.group(1))
                except Exception:
                    hist = []
                sp = tuple(step_to_abstract(s) for s in hist)
                pending = (len(sp), sp)
                continue
            if HIT_RE.search(line) and pending is not None:
                resolve(length, case_id, pending[0], pending[1], gta, True)
                pending = None
        if pending is not None:
            resolve(length, case_id, pending[0], pending[1], gta, False)

# ── Write CSVs ────────────────────────────────────────────────────────────────
with open("a4_divergence_patterns.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["gt_pipeline", "rollout_prefix", "depth", "frequency"])
    for (g, r, d), n in sorted(pat.items(), key=lambda x: -x[1]):
        w.writerow([g, r, d, n])

with open("a4_divergence_by_rollout.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rollout_prefix", "depth", "frequency"])
    for (r, d), n in sorted(by_rollout.items(), key=lambda x: -x[1]):
        w.writerow([r, d, n])

with open("a4_divergence_by_gt_shape.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["gt_pipeline", "divergent_misses", "distinct_cases", "hit_calls",
                "divergent_per_case"])
    rows = [(g, v[0], len(v[1]), v[2]) for g, v in by_gt.items()]
    for g, dm, nc, hc in sorted(rows, key=lambda x: -x[1]):
        per = dm / nc if nc else 0
        w.writerow([g, dm, nc, hc, f"{per:.1f}"])

# ── Console preview ───────────────────────────────────────────────────────────
total_div = sum(pat.values())
print(f"Total divergent misses: {total_div}\n")
print("TOP 20 divergence patterns  [gt_pipeline] => [rollout_prefix] @depth : freq")
print("-" * 84)
for (g, r, d), n in sorted(pat.items(), key=lambda x: -x[1])[:20]:
    print(f"{n:>5}  ({n/total_div*100:4.1f}%)  GT={g:<26} rollout={r:<24} d={d}")
print()
print("TOP 12 GT pipeline SHAPES by divergent misses (which target pipelines hurt most)")
print("-" * 84)
print(f"{'gt_pipeline':<30}{'div_miss':>9}{'cases':>7}{'div/case':>9}{'hits':>7}")
rows = [(g, v[0], len(v[1]), v[2]) for g, v in by_gt.items()]
for g, dm, nc, hc in sorted(rows, key=lambda x: -x[1])[:12]:
    print(f"{g:<30}{dm:>9}{nc:>7}{dm/nc:>9.1f}{hc:>7}")
print("\nWrote: a4_divergence_patterns.csv, a4_divergence_by_rollout.csv, "
      "a4_divergence_by_gt_shape.csv")
