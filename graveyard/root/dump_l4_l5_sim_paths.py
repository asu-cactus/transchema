"""
Dump, for every L4 and L5 case in the a4 (upper_bound) experiment:
  - the ground-truth pipeline (raw operators + abstract bins)
  - the distinct simulated rollout paths (abstract) and how many times each occurred
  - correctness + how many simulate calls got a RAG hint

Output: a4_L4_L5_sim_paths.txt
"""
import ast
import csv
import glob
import os
import re
from collections import Counter, defaultdict

GT_CSV = "ground_truth_pipelines.csv"
RES = "Langraph/results_langraph"
LOG_GLOB = "logs_langraph/mcts_l{L}_p*_rag_ub_partial_a4_pipeline/*.log"
A4_RES = RES + "/mcts_l*_p*_rag_ub_partial_a4_pipeline_*/results_summary.csv"

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


# GT
gt_raw, gt_abs = {}, {}
with open(GT_CSV, encoding="latin-1") as f:
    for row in csv.DictReader(f):
        m = re.match(r"Target(\d+)_(\d+)", row["target_id"])
        if m:
            cid = f"{m.group(1)}_{m.group(2)}"
            gt_raw[cid] = ast.literal_eval(row["operators"])
            gt_abs[cid] = gt_abstract_for(gt_raw[cid])

# correctness
correct = {}
for p in glob.glob(A4_RES):
    with open(p) as f:
        for row in csv.DictReader(f):
            correct[row["case_id"]] = row["is_correct"].strip().lower() == "true"

ITER_RE = re.compile(r"\[simulate\] Iter \d+: mode=\w+, history=(\[.*\])\s*$")
HIT_RE = re.compile(r"\[simulate/pipeline\] RAG hints retrieved for prefix depth=(\d+)")
FNAME_RE = re.compile(r"(\d+)_target(\d+)_MCTS")


def fmt(seq):
    return ">".join(seq) if seq else "(empty)"


# Gather per-case paths/calls/hits for all L4 & L5 cases first.
data = {}   # L -> (calls, hits, paths)
for L in (4, 5):
    calls = defaultdict(int)
    hits = defaultdict(int)
    paths = defaultdict(Counter)
    for path in glob.glob(LOG_GLOB.format(L=L)):
        fm = FNAME_RE.match(os.path.basename(path))
        if not fm:
            continue
        cid = f"{fm.group(1)}_{fm.group(2)}"
        pending = False
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                im = ITER_RE.search(line)
                if im:
                    try:
                        hist = ast.literal_eval(im.group(1))
                    except Exception:
                        hist = []
                    paths[cid][tuple(step_to_abstract(s) for s in hist)] += 1
                    calls[cid] += 1
                    pending = True
                elif HIT_RE.search(line) and pending:
                    hits[cid] += 1
                    pending = False
    data[L] = (calls, hits, paths)


def write_case(out, L, cid, calls, hits, paths):
    c = correct.get(cid)
    verdict = "CORRECT" if c else ("WRONG" if c is False else "n/a")
    out.write("\n" + "-" * 78 + "\n")
    out.write(f"case {cid}  (L{L})   [{verdict}]   "
              f"RAG hits: {hits[cid]}/{calls[cid]} sim calls\n")
    out.write(f"  GT operators : {gt_raw.get(cid, '(absent from GT CSV)')}\n")
    out.write(f"  GT path      : {fmt(gt_abs.get(cid, []))}\n")
    out.write(f"  Simulated paths ({len(paths[cid])} distinct, {calls[cid]} total):\n")
    for p, n in paths[cid].most_common():
        out.write(f"      {n:>4}x  {fmt(p)}\n")


def dump(fname, header_lines, predicate, label):
    with open(fname, "w") as out:
        for line in header_lines:
            out.write(line + "\n")
        out.write("\n")
        for L in (4, 5):
            calls, hits, paths = data[L]
            cids = sorted([c for c in paths if calls[c] > 0 and predicate(c, calls, hits)],
                          key=lambda c: int(c.split("_")[1]))
            out.write("\n" + "#" * 78 +
                      f"\n# LENGTH {L}  ({len(cids)} {label})\n" + "#" * 78 + "\n")
            for cid in cids:
                write_case(out, L, cid, calls, hits, paths)
    print(f"Wrote: {fname}")


# File 1: zero RAG hits
dump(
    "a4_L4_L5_sim_paths_norag.txt",
    ["a4 (upper_bound) experiment — L4 & L5 cases with ZERO RAG hits",
     "=" * 78,
     "Only cases where RAG never hit on any simulate call are included.",
     "For each case: GT pipeline, then each distinct simulated path with its count.",
     "A RAG hit needs gt_abstract[:depth] == rollout_prefix AND len(gt) > depth."],
    lambda c, calls, hits: hits[c] == 0,
    "cases with zero RAG hits",
)

# File 2: all WRONG cases (regardless of RAG hits)
dump(
    "a4_L4_L5_sim_paths_wrong.txt",
    ["a4 (upper_bound) experiment — L4 & L5 cases that were WRONG (incorrect)",
     "=" * 78,
     "All incorrect cases are included, regardless of RAG hit count.",
     "For each case: GT pipeline, then each distinct simulated path with its count."],
    lambda c, calls, hits: correct.get(c) is False,
    "WRONG cases",
)
