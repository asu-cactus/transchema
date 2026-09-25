"""
Deep-dive on the a4 ALWAYS-MISS cases (RAG never hit during simulate).

For each such case, show:
  - the ground-truth pipeline (raw operators + abstract bins)
  - the distinct paths the LLM/MCTS rollouts actually took (abstract, with counts)
  - a discrepancy category explaining why they never align with the single GT entry

A simulate HIT needs gt_abstract[:depth] == rollout_prefix AND len(gt) > depth.
So "always miss" = NONE of the rollout prefixes is a proper prefix of the GT path.
"""
import ast
import csv
import glob
import os
import re
from collections import Counter, defaultdict

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
STRUCT = {"merge", "groupby", "union", "pivot", "unpivot"}


def step_to_abstract(step):
    return _OP_TO_BIN.get(step.split(":")[0].strip().upper(), "other")


def gt_abstract_for(ops):
    steps = [GT_OP_TO_MCTS[o.strip().lower()] for o in ops if o.strip().lower() in GT_OP_TO_MCTS]
    if steps:
        steps.append("NO_MORE_OPERATION")
    return tuple(step_to_abstract(s) for s in steps)


# GT raw operators + abstract
gt_raw, gt_abs = {}, {}
with open(GT_CSV, encoding="latin-1") as f:
    for row in csv.DictReader(f):
        m = re.match(r"Target(\d+)_(\d+)", row["target_id"])
        if not m:
            continue
        cid = f"{m.group(1)}_{m.group(2)}"
        ops = ast.literal_eval(row["operators"])
        gt_raw[cid] = ops
        gt_abs[cid] = gt_abstract_for(ops)

ITER_RE = re.compile(r"\[simulate\] Iter \d+: mode=\w+, history=(\[.*\])\s*$")
HIT_RE = re.compile(r"\[simulate/pipeline\] RAG hints retrieved for prefix depth=(\d+)")
FNAME_RE = re.compile(r"(\d+)_target(\d+)_MCTS")

# case_id -> (total, hits, Counter of rollout abstract paths)
calls = defaultdict(int)
hits = defaultdict(int)
paths = defaultdict(Counter)

for path in glob.glob(LOG_GLOB):
    fm = FNAME_RE.match(os.path.basename(path))
    if not fm:
        continue
    cid = f"{fm.group(1)}_{fm.group(2)}"
    pending = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            im = ITER_RE.search(line)
            if im:
                try:
                    hist = ast.literal_eval(im.group(1))
                except Exception:
                    hist = []
                ab = tuple(step_to_abstract(s) for s in hist)
                calls[cid] += 1
                paths[cid][ab] += 1
                pending = True
                continue
            if HIT_RE.search(line) and pending:
                hits[cid] += 1
                pending = False

always_miss = [c for c in calls if calls[c] > 0 and hits[c] == 0]


def core(seq):
    return tuple(o for o in seq if o != "terminal")


def categorize(cid):
    if cid not in gt_abs:
        return "no_gt_entry"          # case absent from GT CSV -> RAG disabled
    g = core(gt_abs[cid])
    if not g:
        return "no_structural_gt"
    # dominant LLM path
    dom = paths[cid].most_common(1)[0][0]
    l = core(dom)
    if not l:
        return "llm_no_op"            # LLM emitted only NO_MORE_OPERATION
    if l[0] != g[0]:
        return "wrong_first_op"
    if Counter(l) == Counter(g) and l != g:
        return "reorder_same_ops"
    if set(l) <= set(g) and len(l) < len(g):
        return "fewer_ops_granularity"   # right first op, but collapses repeats / stops early
    if set(l) - set(g):
        return "extra_or_wrong_op"
    return "other_prefix_divergence"


cat_counts = Counter(categorize(c) for c in always_miss)

print(f"ALWAYS-MISS cases: {len(always_miss)}\n")
print("Discrepancy categories (by each case's dominant LLM path vs GT):")
for cat, n in cat_counts.most_common():
    print(f"  {n:>4}  {cat}")

# ── Per-case CSV ──────────────────────────────────────────────────────────────
def fmt(seq):
    return ">".join(seq) if seq else "(empty)"


rows = []
for cid in always_miss:
    dom_path, dom_n = paths[cid].most_common(1)[0]
    rows.append((
        cid, int(cid.split("_")[0]),
        str(gt_raw.get(cid, "(absent)")), fmt(gt_abs.get(cid, ())),
        len(paths[cid]),                     # n distinct LLM paths
        fmt(dom_path), dom_n, calls[cid],
        categorize(cid),
    ))
rows.sort(key=lambda r: (r[1], r[0]))
with open("a4_alwaysmiss_paths.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["case_id", "length", "gt_raw_operators", "gt_abstract",
                "n_distinct_llm_paths", "dominant_llm_path", "dominant_path_count",
                "total_sim_calls", "discrepancy_category"])
    w.writerows(rows)
print("\nWrote: a4_alwaysmiss_paths.csv")

# ── Illustrative examples: a few per category ─────────────────────────────────
print("\n" + "=" * 90)
print("ILLUSTRATIVE EXAMPLES  (GT vs the paths the LLM explored)")
print("=" * 90)
by_cat = defaultdict(list)
for c in always_miss:
    by_cat[categorize(c)].append(c)

for cat in ["wrong_first_op", "fewer_ops_granularity", "reorder_same_ops",
            "extra_or_wrong_op", "llm_no_op", "other_prefix_divergence",
            "no_structural_gt", "no_gt_entry"]:
    cs = by_cat.get(cat, [])
    if not cs:
        continue
    print(f"\n### {cat}  ({len(cs)} cases) — showing up to 3:")
    for cid in sorted(cs, key=lambda c: -calls[c])[:3]:
        print(f"\n  case {cid}   (L{cid.split('_')[0]}, {calls[cid]} sim calls)")
        print(f"    GT raw  : {gt_raw.get(cid, '(absent from GT CSV)')}")
        print(f"    GT path : {fmt(gt_abs.get(cid, ()))}")
        print(f"    LLM took ({len(paths[cid])} distinct paths):")
        for p, n in paths[cid].most_common(5):
            print(f"        {n:>3}x  {fmt(p)}")
