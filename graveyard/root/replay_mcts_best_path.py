"""
MCTS Tree Replay Analysis
=========================
Parses tree_viz + action_trace logs from the rag_global_redo experiment,
reconstructs the MCTS tree, and follows three greedy-utility paths at the end
of search (instead of early-stopping):

  greedy-q            : follow child with highest q (average reward)
  greedy-total_reward : follow child with highest total_reward (= q × visits),
                        i.e. the most accumulated reward — THIS IS THE FOCUS
  greedy-best         : follow child with highest best-seen reward

Reports whether the leaf node on each path corresponds to the correct script.

Usage:
    python replay_mcts_best_path.py [--log_dir LOG_DIR] [--min_iters N]
                                    [--output CSV] [--verbose]
"""

import re
import json
import argparse
import csv
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TreeNode:
    depth: int
    op: str
    label: str
    visits: int
    q: float          # average reward = total_reward / visits
    best: float       # best single reward ever seen through this node
    is_best_path: bool
    children: list = field(default_factory=list)
    parent: Optional["TreeNode"] = field(default=None, repr=False)

    @property
    def total_reward(self) -> float:
        """Accumulated reward sum = q × visits (recovers what MCTSNode.total_reward stores)."""
        return self.q * self.visits

    def is_leaf(self):
        return len(self.children) == 0


# ---------------------------------------------------------------------------
# Parsing tree_viz
# ---------------------------------------------------------------------------

ROOT_RE = re.compile(r"\[ROOT\]\s+visits=\s*(\d+)\s+q=([\d.]+)\s+best=([\d.]+)")
NODE_RE = re.compile(
    r"^([\s│]*)[├└]──\s+(\w+)\s+visits=\s*(\d+)\s+q=([\d.]+)\s+best=([\d.]+)(.*?)$"
)


def parse_tree_viz(filepath: Path):
    """Parse a tree_viz file and return the root TreeNode (or None on failure)."""
    text = filepath.read_text(errors="replace")
    lines = text.splitlines()

    root = None
    stack: list[tuple[int, TreeNode]] = []  # (depth, node)
    prev_node: Optional[TreeNode] = None
    expecting_label = False

    for line in lines:
        raw = line.rstrip()

        # ── Root ──────────────────────────────────────────────────────────
        m = ROOT_RE.search(raw)
        if m:
            root = TreeNode(
                depth=0, op="ROOT", label="ROOT",
                visits=int(m.group(1)), q=float(m.group(2)), best=float(m.group(3)),
                is_best_path=False,
            )
            stack = [(0, root)]
            prev_node = root
            expecting_label = False
            continue

        # ── Child node ────────────────────────────────────────────────────
        m = NODE_RE.match(raw)
        if m and "visits=" in raw:
            prefix = m.group(1)
            depth = prefix.count("│") + 1
            op = m.group(2)
            visits = int(m.group(3))
            q = float(m.group(4))
            best = float(m.group(5))
            tail = m.group(6)
            is_best = "best path" in tail

            node = TreeNode(
                depth=depth, op=op, label="",
                visits=visits, q=q, best=best,
                is_best_path=is_best,
            )

            # Pop stack until we find the parent (depth - 1)
            while stack and stack[-1][0] >= depth:
                stack.pop()
            if stack:
                parent = stack[-1][1]
                parent.children.append(node)
                node.parent = parent

            stack.append((depth, node))
            prev_node = node
            expecting_label = True
            continue

        # ── Label line (the detailed op description following a node line) ─
        stripped = raw.strip()
        if (
            expecting_label
            and prev_node is not None
            and stripped
            and not stripped.startswith("=")
            and not stripped.startswith("MCTS")
            and "├──" not in stripped
            and "└──" not in stripped
            and "visits=" not in stripped
            and "[ROOT]" not in stripped
        ):
            if not prev_node.label:
                prev_node.label = stripped
            expecting_label = False  # only one label per node

    return root


# ---------------------------------------------------------------------------
# Greedy-path selection
# ---------------------------------------------------------------------------

def _key_fn(utility: str):
    """Return a child-scoring key function for the given utility name."""
    if utility == "total_reward":
        # Accumulated reward sum (q × visits). Tie-break: most visits.
        return lambda c: (c.total_reward, c.visits)
    elif utility == "best":
        return lambda c: (c.best, c.visits)
    else:  # "q"
        return lambda c: (c.q, c.visits)


def greedy_path(root: TreeNode, utility: str = "total_reward") -> list[TreeNode]:
    """Follow the child with the highest utility at every node until a leaf.

    utility choices:
      'total_reward'  most accumulated reward (q × visits)  ← primary focus
      'q'             highest average reward
      'best'          highest single reward ever seen
    """
    path = [root]
    node = root
    key = _key_fn(utility)
    while node.children:
        node = max(node.children, key=key)
        path.append(node)
    return path


def best_on_path(path: list[TreeNode]) -> tuple[float, TreeNode]:
    """Return (best_score, best_node) for the node with highest 'best' on the path."""
    best_node = max(path, key=lambda n: (n.best, n.visits))
    return best_node.best, best_node


# ---------------------------------------------------------------------------
# Parse action_trace for summary
# ---------------------------------------------------------------------------

ITER_RE = re.compile(r"Total iterations\s*:\s*(\d+)")
SCORE_RE = re.compile(r"Best score\s*:\s*([\d.]+)")
HIST_RE = re.compile(r"Best history\s*:\s*(\[.*\])")


def parse_action_trace(filepath: Path) -> dict:
    text = filepath.read_text(errors="replace")
    result = {"total_iters": None, "best_score": None, "best_history": None}
    m = ITER_RE.search(text)
    if m:
        result["total_iters"] = int(m.group(1))
    m = SCORE_RE.search(text)
    if m:
        result["best_score"] = float(m.group(1))
    m = HIST_RE.search(text)
    if m:
        try:
            result["best_history"] = json.loads(m.group(1).replace("'", '"'))
        except Exception:
            result["best_history"] = m.group(1)
    return result


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def _path_stats(path: list[TreeNode], label: str) -> dict:
    """Extract leaf stats and best-on-path for one greedy path."""
    leaf = path[-1]
    bop_score, _ = best_on_path(path)
    op_seq = [n.label or n.op for n in path[1:]]  # skip ROOT
    return {
        f"{label}_depth":        len(path) - 1,
        f"{label}_leaf_tr":      round(leaf.total_reward, 4),   # total_reward at leaf
        f"{label}_leaf_q":       round(leaf.q, 4),
        f"{label}_leaf_best":    round(leaf.best, 4),
        f"{label}_leaf_visits":  leaf.visits,
        f"{label}_leaf_correct": leaf.best >= 0.9,
        f"{label}_bop_best":     round(bop_score, 4),
        f"{label}_bop_correct":  bop_score >= 0.9,
        f"{label}_op_seq":       " → ".join(op_seq),
    }


def analyse_case(case_dir: Path) -> list[dict] | None:
    """Analyse one case directory. Returns a list of per-case result dicts."""
    tree_files = sorted(case_dir.glob("tree_viz_*.txt"))
    if not tree_files:
        return None

    results = []
    for tf in tree_files:
        case_id = tf.stem.replace("tree_viz_", "")
        at_file = case_dir / f"action_trace_{case_id}.txt"
        if not at_file.exists():
            continue

        root = parse_tree_viz(tf)
        if root is None:
            continue

        summary = parse_action_trace(at_file)

        # Three greedy paths
        path_tr   = greedy_path(root, utility="total_reward")
        path_q    = greedy_path(root, utility="q")
        path_best = greedy_path(root, utility="best")

        result = {
            "case_dir":      str(case_dir.name),
            "case_id":       case_id,
            # Early-stopping baseline
            "es_iters":      summary["total_iters"],
            "es_best_score": summary["best_score"],
            "es_correct":    (summary["best_score"] or 0.0) >= 0.9,
            # Tree root stats
            "root_visits":   root.visits,
            "root_tr":       round(root.total_reward, 4),
            "root_best":     round(root.best, 4),
        }
        result.update(_path_stats(path_tr,   "tr"))    # total_reward path (MAIN)
        result.update(_path_stats(path_q,    "gq"))    # average-reward path
        result.update(_path_stats(path_best, "gb"))    # best-seen path
        results.append(result)

    return results


def _pct(n, total):
    return f"{n:3d} / {total} = {n/total:.1%}"


def extract_length_from_id(case_id: str) -> str:
    """Extract the pipeline length label from the case_id (e.g. '5_17' → 'l5')."""
    m = re.match(r'^(\d+)_', case_id)
    if m:
        return f"l{m.group(1)}"
    return "other"


def dir_priority(case_dir_name: str) -> int:
    """Lower priority value = preferred when deduplicating (canonical dirs first)."""
    if re.match(r'^cases_l\d+_p\d+$', case_dir_name):
        return 0  # canonical: cases_lN_pM (no suffix)
    if re.match(r'^cases_l\d+_', case_dir_name):
        return 1  # e.g. cases_l4_early_pN
    return 2      # reruns, o4mini, c75, etc.


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log_dir",
        default="logs_langraph/rag_global_redo",
        help="Root log directory (default: logs_langraph/rag_global_redo)",
    )
    parser.add_argument(
        "--min_iters", type=int, default=1,
        help="Skip cases with fewer total iterations (default: 1 = include all)",
    )
    parser.add_argument(
        "--output", default="mcts_replay_results.csv",
        help="Output CSV filename",
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--no_filter", action="store_true",
        help="Include all case subdirectories (skip canonical cases_lN_pM filter)",
    )
    args = parser.parse_args()

    log_dir = Path(args.log_dir)
    if not log_dir.exists():
        print(f"[ERROR] Log directory not found: {log_dir}")
        return

    # By default only include canonical gpt-4.1-mini experiment dirs: cases_lN_pM
    # Use --no_filter to include all subdirectories (e.g. cases_cN naming)
    CANONICAL_RE = re.compile(r'^cases_l\d+_p\d+$')
    case_dirs = sorted(
        d for d in log_dir.iterdir()
        if d.is_dir() and (args.no_filter or CANONICAL_RE.match(d.name))
    )
    print(f"Found {len(case_dirs)} case directories in {log_dir}")

    all_results = []
    skipped_no_tree = 0
    skipped_few_iters = 0

    for case_dir in case_dirs:
        case_results = analyse_case(case_dir)
        if case_results is None:
            skipped_no_tree += 1
            continue
        for r in case_results:
            if (r["es_iters"] or 0) < args.min_iters:
                skipped_few_iters += 1
                continue
            r["_dir_priority"] = dir_priority(r["case_dir"])
            all_results.append(r)
            if args.verbose:
                es_tag  = "✓" if r["es_correct"]         else "✗"
                tr_tag  = "✓" if r["tr_leaf_correct"]     else "✗"
                bop_tag = "✓" if r["tr_bop_correct"]      else "✗"
                print(
                    f"  {r['case_id']:10s}  "
                    f"es={es_tag}({r['es_iters']}i,{r['es_best_score']:.2f})  "
                    f"TR_leaf={tr_tag}(best={r['tr_leaf_best']:.3f},tr={r['tr_leaf_tr']:.3f})  "
                    f"TR_bop={bop_tag}({r['tr_bop_best']:.3f})  "
                    f"depth={r['tr_depth']}"
                )

    if not all_results:
        print("No results to report.")
        return

    # Deduplicate by case_id: prefer canonical dirs (priority 0) over reruns
    all_results.sort(key=lambda r: (r["case_id"], r["_dir_priority"]))
    seen_ids: set = set()
    deduped = []
    dup_count = 0
    for r in all_results:
        if r["case_id"] in seen_ids:
            dup_count += 1
            continue
        seen_ids.add(r["case_id"])
        r["length"] = extract_length_from_id(r["case_id"])
        deduped.append(r)
    all_results = deduped
    if dup_count:
        print(f"Removed {dup_count} duplicate case entries (kept canonical dir version).")

    n = len(all_results)

    def cnt(pred):
        return sum(1 for r in all_results if pred(r))

    es_ok  = cnt(lambda r: r["es_correct"])
    tr_ok  = cnt(lambda r: r["tr_leaf_correct"])    # total_reward → leaf best
    tr_bop = cnt(lambda r: r["tr_bop_correct"])     # total_reward → best on path
    gq_ok  = cnt(lambda r: r["gq_leaf_correct"])
    gq_bop = cnt(lambda r: r["gq_bop_correct"])
    gb_ok  = cnt(lambda r: r["gb_leaf_correct"])

    # Confusion vs early-stopping for the main (total_reward) strategy
    both   = cnt(lambda r: r["es_correct"] and r["tr_leaf_correct"])
    es_only = cnt(lambda r: r["es_correct"] and not r["tr_leaf_correct"])
    tr_only = cnt(lambda r: not r["es_correct"] and r["tr_leaf_correct"])
    neither = cnt(lambda r: not r["es_correct"] and not r["tr_leaf_correct"])

    bop_still_miss = cnt(lambda r: r["es_correct"] and not r["tr_bop_correct"])

    W = 65
    print(f"\n{'='*W}")
    print(f"MCTS Replay Analysis — {n} cases  (min_iters≥{args.min_iters})")
    print(f"{'='*W}")
    print(f"  Skipped (no tree_viz) : {skipped_no_tree}")
    print(f"  Skipped (few iters)   : {skipped_few_iters}")
    print(f"{'─'*W}")
    print(f"  Strategy                             Leaf correct    BOP correct")
    print(f"  {'─'*60}")
    print(f"  Early-stopping (baseline)          {_pct(es_ok, n)}")
    print(f"  Greedy total_reward  (q×visits) ►  {_pct(tr_ok, n)}   {_pct(tr_bop, n)}")
    print(f"  Greedy q (avg reward)              {_pct(gq_ok, n)}   {_pct(gq_bop, n)}")
    print(f"  Greedy best-seen                   {_pct(gb_ok, n)}")
    print(f"{'─'*W}")
    print(f"  [total_reward path vs early-stopping]")
    print(f"  ES✓ ∧ TR✓  (both correct)          {both:3d}")
    print(f"  ES✓ ∧ TR✗  (TR misses at leaf)     {es_only:3d}  ← ES needed")
    print(f"  ES✓ ∧ TR_BOP✗ (still missed)       {bop_still_miss:3d}  ← irreducible")
    print(f"  ES✗ ∧ TR✓  (TR recovers)            {tr_only:3d}  ← TR wins")
    print(f"  ES✗ ∧ TR✗  (both miss)              {neither:3d}")
    print(f"{'='*W}")

    # ── Per-length breakdown ───────────────────────────────────────────────────
    from collections import defaultdict
    by_len = defaultdict(list)
    for r in all_results:
        by_len[r["length"]].append(r)

    print(f"\n{'='*W}")
    print(f"Per-length breakdown")
    print(f"{'='*W}")
    print(f"  {'Length':8s}  {'Cases':>5s}  {'ES correct':>14s}  {'TR leaf':>14s}  {'TR BOP':>14s}")
    print(f"  {'─'*70}")
    for length in sorted(by_len, key=lambda x: (x == "other", x)):
        rows = by_len[length]
        ln = len(rows)
        l_es  = sum(1 for r in rows if r["es_correct"])
        l_tr  = sum(1 for r in rows if r["tr_leaf_correct"])
        l_bop = sum(1 for r in rows if r["tr_bop_correct"])
        print(
            f"  {length:8s}  {ln:5d}  "
            f"{l_es:3d}/{ln} ({l_es/ln:.0%})  "
            f"{l_tr:3d}/{ln} ({l_tr/ln:.0%})  "
            f"{l_bop:3d}/{ln} ({l_bop/ln:.0%})"
        )
    print(f"  {'─'*70}")
    print(
        f"  {'TOTAL':8s}  {n:5d}  "
        f"{es_ok:3d}/{n} ({es_ok/n:.0%})  "
        f"{tr_ok:3d}/{n} ({tr_ok/n:.0%})  "
        f"{tr_bop:3d}/{n} ({tr_bop/n:.0%})"
    )
    print(f"{'='*W}")

    # Detail: TR leaf misses
    if es_only:
        print(f"\nCases where ES found correct but TR-leaf MISSES ({es_only}):")
        for r in all_results:
            if r["es_correct"] and not r["tr_leaf_correct"]:
                bop_tag = "BOP✓" if r["tr_bop_correct"] else "BOP✗"
                print(
                    f"  {r['case_id']:10s}  es={r['es_best_score']:.2f}  "
                    f"leaf_best={r['tr_leaf_best']:.3f}  leaf_tr={r['tr_leaf_tr']:.3f}  "
                    f"{bop_tag}({r['tr_bop_best']:.3f})  "
                    f"path={r['tr_op_seq'][:70]}"
                )

    # Detail: TR recovers what ES missed
    if tr_only:
        print(f"\nCases where ES MISSED but TR-leaf recovers ({tr_only}):")
        for r in all_results:
            if not r["es_correct"] and r["tr_leaf_correct"]:
                print(
                    f"  {r['case_id']:10s}  es={r['es_best_score']:.2f}  "
                    f"leaf_best={r['tr_leaf_best']:.3f}"
                )

    # ── CSV ────────────────────────────────────────────────────────────────
    out_path = Path(args.output)
    csv_rows = [{k: v for k, v in r.items() if k != "_dir_priority"} for r in all_results]
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"\nDetailed results → {out_path}")


if __name__ == "__main__":
    main()
