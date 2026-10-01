#!/usr/bin/env python3
"""
Mean nodes expanded (Ablation Plan, expansion-policy / lambda ablation table):
for each case in a two-phase run_github_mcts_dmx.sh / run_smartbuilding_v2_mcts20_dmx.sh
result+log pair, how many MCTS tree nodes were created before the pipeline
that was ultimately RETURNED (results_summary.csv's operation_history) was
first generated during search.

METHOD
------
Every MCTS expansion iteration logs one line per new child node:
    "[expand] Iter N: added <OP> cfg=<CFG> ... (tree now has K children)"
Each such line is one new node, in chronological order, globally across the
whole search (not just along the winning path) -- counting them gives the
running tree size at any point in the log.

The point a specific pipeline gets simulated is logged separately:
    "[simulate/pipeline] Parsed complete plan: [<op1>, <op2>, ..., 'NO_MORE_OPERATION']"
This list, when it matches operation_history, tells us exactly when (in terms
of node-count-so-far) the final returned pipeline was first generated.

"nodes expanded before return" for a case = the running "added" counter at
the first "Parsed complete plan" line whose list matches operation_history.

MATCHING MODES
--------------
--exact            require the plan list to equal operation_history exactly
                    (ast.literal_eval both, compare as Python lists)
--fuzzy T           accept the FIRST plan line whose text similarity to
                    operation_history (difflib.SequenceMatcher ratio on the
                    " | ".join()'d strings) is >= T. Use this when the LLM
                    re-serializes an equivalent pipeline with minor formatting
                    differences (whitespace, quoting, trivial rephrasing)
                    across iterations -- exact match alone misses those.

COVERAGE CAVEAT (read before reporting a number)
-------------------------------------------------
Not every case resolves. The main cause: when CRITIQUE repairs a pipeline
mid-search, the repaired script can become the new best_script via a
DIFFERENT code path (nodes.py's mcts_critique node, building tree nodes
through _find_or_create_path from the critique's own proposed plan) that
never logs a "Parsed complete plan" line at all. Such cases have literally
no candidate line to match against, at any fuzzy threshold -- they are
correctly reported as unresolved, not silently misattributed. Observed
unresolved rates on the original (lambda=0, lambda=1, tau=0.8) runs were
~10-16%, split roughly evenly between "has a plan line but none match even
loosely" and "has zero plan lines" (the critique-only path). If your
unresolved rate here is wildly different (e.g. >30%), something about this
run's logging or case layout may differ -- sanity check before trusting the
average.

The "--fuzzy" coverage gain over "--exact" is usually small (a handful of
cases per ~700) -- most unresolved cases simply have no plan line to begin
with, so loosening the match threshold does not recover them. Expect most of
the benefit of fuzzy matching to show up as a LOWER average among cases that
were already resolved (because it now accepts the FIRST near-match, which
can occur earlier than the first byte-exact match), not as much higher n.

USAGE
-----
Exact match, one config:
    python3 analyze_nodes_expanded.py \\
        --log-root logs_langraph/github_abl_lambda01_lam0_gh_leafstop_dmx-gpt-oss-120b \\
        --result-dir Langraph/results_langraph/github_abl_lambda01_lam0_gh_leafstop_dmx-gpt-oss-120b \\
        --label "GH lam0" --exact

Fuzzy match at one threshold, with per-length breakdown:
    python3 analyze_nodes_expanded.py --log-root ... --result-dir ... \\
        --label "GH lam025" --fuzzy 0.9 --by-length

Multiple thresholds in one pass (efficient -- single log scan per case):
    python3 analyze_nodes_expanded.py --log-root ... --result-dir ... \\
        --label "GH lam025" --fuzzy 0.7 0.8 0.9 0.95

Total tree size instead (no matching at all -- just every case's full node
count over its whole search, 100% coverage since nothing needs to match):
    python3 analyze_nodes_expanded.py --log-root ... --label "GH lam025" --total-only

Log-file layout this expects (same as every run_*_mcts_dmx.sh launcher writes):
    <log_root>/cases_g<L>_c<C>/<L>_target<C>_MCTS_<timestamp>.log
    <result_dir>/*/results_summary.csv   (case_id, operation_history columns)
"""
import argparse
import ast
import csv
import difflib
import glob
import os
import re
from collections import defaultdict

ADDED_RE = re.compile(r"\[expand\] Iter \d+: added ")
PLAN_RE = re.compile(r"\[simulate/pipeline\] Parsed complete plan: (\[.*\])\s*$")


def load_case_histories(result_dir):
    """case_id -> operation_history (list[str]) from every results_summary.csv under result_dir."""
    out = {}
    for f in glob.glob(f"{result_dir}/*/results_summary.csv"):
        with open(f, newline="") as fh:
            for row in csv.DictReader(fh):
                cid = row.get("case_id")
                hist = row.get("operation_history")
                if not cid or not hist:
                    continue
                try:
                    out[cid] = ast.literal_eval(hist)
                except (ValueError, SyntaxError):
                    continue
    return out


def find_case_log(log_root, group, case):
    cand = glob.glob(f"{log_root}/cases_g{group}_c{case}/*_MCTS_*.log")
    if not cand:
        return None
    cand.sort(key=os.path.getmtime)
    return cand[-1]  # most recent, in case of a retried/overwritten case dir


def _joined(plan):
    return " | ".join(str(s) for s in plan)


def nodes_before_return(log_path, target_history, thresholds):
    """
    thresholds: iterable of floats; 1.0 means "exact match" (a similarity
    ratio of 1.0 IS an exact match, so pass [1.0] for --exact).
    Returns {threshold: node_count_or_None}, single pass over the file.
    """
    target_str = _joined(target_history)
    result = {t: None for t in thresholds}
    remaining = sorted(thresholds)
    count = 0
    try:
        with open(log_path, "r", errors="replace") as fh:
            for line in fh:
                if ADDED_RE.search(line):
                    count += 1
                    continue
                if not remaining:
                    continue
                m = PLAN_RE.search(line)
                if not m:
                    continue
                try:
                    plan = ast.literal_eval(m.group(1))
                except (ValueError, SyntaxError):
                    continue
                if remaining and remaining[0] == 1.0:
                    sim = 1.0 if plan == target_history else 0.0
                else:
                    sim = difflib.SequenceMatcher(None, _joined(plan), target_str).ratio()
                newly = [t for t in remaining if sim >= t]
                for t in newly:
                    result[t] = count
                remaining = [t for t in remaining if t not in newly]
    except FileNotFoundError:
        pass
    return result


def total_tree_nodes(log_path):
    count = 0
    try:
        with open(log_path, "r", errors="replace") as fh:
            for line in fh:
                if ADDED_RE.search(line):
                    count += 1
    except FileNotFoundError:
        return None
    return count


def run_matching(log_root, result_dir, label, thresholds, by_length):
    histories = load_case_histories(result_dir)
    resolved = {t: [] for t in thresholds}
    resolved_by_length = {t: defaultdict(list) for t in thresholds}
    unresolved = {t: 0 for t in thresholds}

    for case_id, hist in histories.items():
        try:
            group, case = case_id.split("_", 1)
        except ValueError:
            continue
        L = int(group)
        if hist == ["NO_MORE_OPERATION"] or len(hist) == 0:
            for t in thresholds:
                resolved[t].append(0)
                resolved_by_length[t][L].append(0)
            continue
        log_path = find_case_log(log_root, group, case)
        if log_path is None:
            continue
        res = nodes_before_return(log_path, hist, thresholds)
        for t in thresholds:
            if res[t] is None:
                unresolved[t] += 1
            else:
                resolved[t].append(res[t])
                resolved_by_length[t][L].append(res[t])

    print(f"=== {label} ===")
    for t in thresholds:
        tag = "exact" if t == 1.0 else f"fuzzy>={t}"
        vals = resolved[t]
        avg = sum(vals) / len(vals) if vals else float("nan")
        print(f"  [{tag}] n_resolved={len(vals)} unresolved={unresolved[t]} avg_nodes_before_return={avg:.2f}")
        if by_length:
            for L in sorted(resolved_by_length[t].keys()):
                v = resolved_by_length[t][L]
                a = sum(v) / len(v) if v else float("nan")
                print(f"      L{L}: avg={a:.2f} n={len(v)}")


def run_total(log_root, label, by_length):
    by_length_vals = defaultdict(list)
    all_vals = []
    for cd in glob.glob(f"{log_root}/cases_g*_c*"):
        m = re.match(r"cases_g(\d+)_c(\d+)", os.path.basename(cd))
        if not m:
            continue
        group, case = m.group(1), m.group(2)
        log_path = find_case_log(log_root, group, case)
        if log_path is None:
            continue
        n = total_tree_nodes(log_path)
        if n is None:
            continue
        by_length_vals[int(group)].append(n)
        all_vals.append(n)
    print(f"=== {label} (total tree size, full coverage) ===")
    overall = sum(all_vals) / len(all_vals) if all_vals else float("nan")
    print(f"  OVERALL: avg={overall:.2f} n={len(all_vals)}")
    if by_length:
        for L in sorted(by_length_vals.keys()):
            v = by_length_vals[L]
            print(f"  L{L}: avg={sum(v)/len(v):.2f} n={len(v)}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--log-root", required=True, help="e.g. logs_langraph/github_abl_lambda_lam025_gh_leafstop_dmx-gpt-oss-120b")
    p.add_argument("--result-dir", help="e.g. Langraph/results_langraph/github_abl_lambda_lam025_gh_leafstop_dmx-gpt-oss-120b (required unless --total-only)")
    p.add_argument("--label", required=True)
    p.add_argument("--exact", action="store_true", help="require exact list match (threshold=1.0)")
    p.add_argument("--fuzzy", nargs="+", type=float, metavar="T", help="one or more similarity thresholds, e.g. --fuzzy 0.7 0.8 0.9 0.95")
    p.add_argument("--by-length", action="store_true", help="also print the per-length (benchmark 'L' label) breakdown")
    p.add_argument("--total-only", action="store_true", help="skip matching entirely; report total tree size per case (100% coverage, no result-dir needed)")
    args = p.parse_args()

    if args.total_only:
        run_total(args.log_root, args.label, args.by_length)
        return

    if not args.result_dir:
        p.error("--result-dir is required unless --total-only is set")

    thresholds = []
    if args.exact:
        thresholds.append(1.0)
    if args.fuzzy:
        thresholds.extend(args.fuzzy)
    if not thresholds:
        thresholds = [1.0]  # default to exact if nothing specified

    run_matching(args.log_root, args.result_dir, args.label, sorted(set(thresholds)), args.by_length)


if __name__ == "__main__":
    main()
