"""
MCTS Tree Reconstruction from Log Files
=========================================
Parses the detailed MCTS *.log files written to each case directory and
reconstructs the MCTS tree WITHOUT needing a tree_viz file.

This is useful when the experiment crashed or timed out before writing tree_viz
(the normal output of a complete run).

Reconstruction method
---------------------
Each MCTS iteration logs:
  [MCTS Select]        — which node was selected (depth, op)
  [expand]             — which children were added + which child was simulated
  [simulate]           — rollout_history (exact path from ROOT to expanded child)
  [simulate/pipeline]  — the LLM's generated plan (current_full_history)
  [execute_and_score]  — reward (pre_critique_score)
  [_run_critique_llm]  — critique plan
  [mcts_critique]      — critique score (S → S2), critique path node count + capped depth
  [backpropagate]      — which paths got which rewards, root.visits as ground-truth check

The script replays every backpropagation step to compute per-node
visits / total_reward / best_score, then runs the same greedy-path analysis
as replay_mcts_best_path.py.

Usage
-----
    python replay_mcts_from_log.py [--log_dir DIR] [--no_filter] [--output CSV] [--verbose]
"""

import re
import ast
import csv
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Tree node
# ---------------------------------------------------------------------------

@dataclass
class ReconNode:
    """A reconstructed MCTS tree node."""
    op: str          # operator type label (e.g. "JOIN")
    cfg: str         # full configured step string (updated as more log lines seen)
    depth: int
    visits: int = 0
    total_reward: float = 0.0
    best: float = 0.0
    children: dict = field(default_factory=dict)        # cfg (or prefix) → ReconNode
    parent: Optional["ReconNode"] = field(default=None, repr=False)

    @property
    def q(self) -> float:
        return self.total_reward / self.visits if self.visits > 0 else 0.0

    @property
    def total_reward_prop(self) -> float:
        return self.q * self.visits  # same as total_reward

    def is_leaf(self) -> bool:
        return len(self.children) == 0


# ---------------------------------------------------------------------------
# Tree helpers
# ---------------------------------------------------------------------------

def _child_key(cfg: str) -> str:
    """80-char prefix used as the lookup key, matching how the log truncates."""
    return cfg[:80]


def _lookup_child(parent: ReconNode, cfg: str) -> Optional[ReconNode]:
    """
    Find a child by exact key first, then by 80-char prefix match.
    When a longer cfg is seen for an existing truncated key, the entry is updated.
    """
    if cfg in parent.children:
        return parent.children[cfg]
    key80 = _child_key(cfg)
    for existing_key, child in list(parent.children.items()):
        if _child_key(existing_key) == key80:
            if len(cfg) > len(existing_key):
                # Upgrade truncated key → full cfg
                parent.children[cfg] = parent.children.pop(existing_key)
                child.cfg = cfg
            return child
    return None


def _get_or_create_child(parent: ReconNode, cfg: str) -> ReconNode:
    child = _lookup_child(parent, cfg)
    if child is None:
        op_type = cfg.split(":")[0].strip().split(" ")[0]
        child = ReconNode(op=op_type, cfg=cfg, depth=parent.depth + 1)
        child.parent = parent
        parent.children[cfg] = child
    return child


def find_or_create_path(root: ReconNode, ops: list) -> list:
    """
    Walk (and create if needed) the path defined by ops from root.
    Returns list of nodes [root, node_op1, node_op1+op2, ...].
    """
    path = [root]
    node = root
    for op in ops:
        node = _get_or_create_child(node, op)
        path.append(node)
    return path


# ---------------------------------------------------------------------------
# GROUP_BY/AGGREGATE splitting (mirrors nodes.py _split_groupby_aggregate)
# ---------------------------------------------------------------------------

_GBA_RE1_GB  = re.compile(r'"group_by"\s*=\s*(\[.*?\])')
_GBA_RE1_AGG = re.compile(r'"aggregations"\s*=\s*(\[.*\])\s*$', re.DOTALL)
_GBA_RE2_GB  = re.compile(r'group_by=(\[.*?\])')
_GBA_RE2_AGG = re.compile(r'aggregations=(\[.*\])\s*$', re.DOTALL)


def _split_gba(history: list) -> list:
    """Split GROUP_BY/AGGREGATE steps into separate GROUP_BY + AGGREGATE nodes."""
    result = []
    for step in history:
        if "GROUP_BY/AGGREGATE" not in step:
            result.append(step)
            continue
        after = step.split(":", 1)[1].strip() if ":" in step else step
        m_gb  = _GBA_RE1_GB.search(after)
        m_agg = _GBA_RE1_AGG.search(after)
        if m_gb and m_agg:
            result.append(f"GROUP_BY : {m_gb.group(1)}")
            result.append(f"AGGREGATE : {m_agg.group(1).strip()}")
            continue
        m_gb  = _GBA_RE2_GB.search(after)
        m_agg = _GBA_RE2_AGG.search(after)
        if m_gb and m_agg:
            result.append(f"GROUP_BY : {m_gb.group(1)}")
            result.append(f"AGGREGATE : {m_agg.group(1).strip()}")
            continue
        result.append(step)  # cannot parse — pass through
    return result


# ---------------------------------------------------------------------------
# Log parsing regexes
# ---------------------------------------------------------------------------

RE_SELECT       = re.compile(r'\[MCTS Select\] Iter (\d+): selected depth=(\d+), op=(\S+)')
RE_EXPAND_ADD   = re.compile(r'\[expand\] Iter (\d+): added (?:child|hints_v3 \w+) (?:op=\w+ )?cfg=(.+?) \((?:tree now|$)')
RE_EXPAND_SIM   = re.compile(r'\[expand\] Iter (\d+): simulating top-priority op=\w+ \| cfg=(.+?) \(\d+ new child')
RE_SIMULATE     = re.compile(r'\[simulate\] Iter (\d+): mode=\w+, history=(\[.*\])')
RE_PIPELINE     = re.compile(r'\[simulate/pipeline\] Parsed complete plan: (\[.*\])')
RE_REUSE        = re.compile(r'\[reuse_terminal\] Iter (\d+)')
RE_SCORE        = re.compile(r'\[execute_and_score\] Iter (\d+): reward=([\d.]+).*history=(\[.*\])')
RE_CRIT_PLAN    = re.compile(r'\[_run_critique_llm\] Parsed critique plan: (\[.*\])')
RE_CRIT_SCORE   = re.compile(r'\[mcts_critique\] Iter (\d+): score [\d.]+ → ([\d.]+)')
RE_CRIT_PATH    = re.compile(r'\[mcts_critique\] Critique path created: (\d+) nodes \(plan_len=\d+ → capped at depth=(\d+)\)')
RE_BP_DIVERGE   = re.compile(r'\[backpropagate\] Iter (\d+): sim path diverged.*giving (\d+) selection-only nodes')
RE_BP_P1        = re.compile(r'\[backpropagate\] Iter (\d+): Pass 1 \((\w+) path\): (\d+) nodes, reward=([\d.]+)')
RE_BP_P2        = re.compile(r'\[backpropagate\] Iter (\d+): Pass 2 \(critique path\): (\d+) nodes, reward=([\d.]+)')
RE_BP_DONE      = re.compile(r'\[backpropagate\] Iter (\d+) done\. pre_critique_reward=([\d.]+), critique_reward=([\d.]+), root\.visits=(\d+)')
RE_COMPLETE     = re.compile(r'\[MCTS(?: Complete| Complete\]).*best_score=([\d.]+)')
RE_COMPLETE2    = re.compile(r'\[MCTS\] Search complete\. best_score=([\d.]+)')


def _parse_list(s: str) -> list:
    """Parse a Python list literal from a log string, tolerating truncation."""
    try:
        return ast.literal_eval(s)
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Core log parser — returns reconstructed root node + summary
# ---------------------------------------------------------------------------

def parse_log(filepath: Path) -> tuple:
    """
    Parse one MCTS log file and reconstruct the tree.
    Returns (root: ReconNode, best_score: float, total_iters: int).
    Returns (None, 0.0, 0) on failure.
    """
    try:
        text = filepath.read_text(errors="replace")
    except Exception:
        return None, 0.0, 0

    lines = text.splitlines()

    root = ReconNode(op="ROOT", cfg="ROOT", depth=0)

    # Per-iteration accumulator — reset on each new iteration
    cur: dict = {}

    def _reset():
        return {
            "iter":              -1,
            "rollout_history":   None,   # from [simulate] or [execute_and_score]
            "llm_plan":          None,   # from [simulate/pipeline]
            "pre_score":         0.0,
            "critique_plan":     None,
            "critique_cap":      0,      # capped depth
            "critique_score":    0.0,
            "diverged":          False,
            "n_sel_only":        0,
            "has_critique":      False,
            "is_reuse":          False,
            "expand_children":   [],     # (cfg80,) added to parent
        }

    cur = _reset()

    best_score = 0.0
    total_iters = 0

    for line in lines:
        # ── Select ─────────────────────────────────────────────────────────
        m = RE_SELECT.search(line)
        if m:
            it = int(m.group(1))
            if it != cur["iter"] and cur["iter"] >= 0:
                # Should have been finalised by BP_DONE — safety: ignore stale
                pass
            cur["iter"] = it
            cur["expand_children"] = []
            continue

        # ── Expand: added child ────────────────────────────────────────────
        m = RE_EXPAND_ADD.search(line)
        if m and cur["iter"] >= 0:
            cfg_prefix = m.group(2).strip()
            cur["expand_children"].append(cfg_prefix)
            continue

        # ── Expand: simulating top-priority child ──────────────────────────
        m = RE_EXPAND_SIM.search(line)
        if m and cur["iter"] >= 0:
            # cfg80 of the child actually being simulated (recorded but not
            # used in reconstruction — rollout_history from [simulate] is
            # the authoritative path)
            pass

        # ── Reuse terminal ─────────────────────────────────────────────────
        m = RE_REUSE.search(line)
        if m:
            cur["is_reuse"] = True
            continue

        # ── Simulate history ───────────────────────────────────────────────
        m = RE_SIMULATE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            cur["rollout_history"] = _split_gba(_parse_list(m.group(2)))
            # Now we know the parent of the expanded child; add expand children
            # to the parent node in the tree.
            rollout = cur["rollout_history"]
            if rollout:
                parent_path_ops = rollout[:-1]
                parent_node = find_or_create_path(root, parent_path_ops)[-1]
                for cfg_prefix in cur["expand_children"]:
                    _get_or_create_child(parent_node, cfg_prefix)
            continue

        # ── Pipeline parsed plan (LLM actual output) ───────────────────────
        m = RE_PIPELINE.search(line)
        if m:
            cur["llm_plan"] = _split_gba(_parse_list(m.group(1)))
            continue

        # ── Score ──────────────────────────────────────────────────────────
        m = RE_SCORE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            cur["pre_score"] = float(m.group(2))
            if cur["rollout_history"] is None:
                # Fallback: use history from score line (covers reuse + failed sim)
                cur["rollout_history"] = _split_gba(_parse_list(m.group(3)))
            r = float(m.group(2))
            if r > best_score:
                best_score = r
            continue

        # ── Critique plan ──────────────────────────────────────────────────
        m = RE_CRIT_PLAN.search(line)
        if m:
            cur["critique_plan"] = _split_gba(_parse_list(m.group(1)))
            continue

        # ── Critique score S → S2 ──────────────────────────────────────────
        m = RE_CRIT_SCORE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            cur["critique_score"] = float(m.group(2))
            continue

        # ── Critique path info ─────────────────────────────────────────────
        m = RE_CRIT_PATH.search(line)
        if m:
            cur["has_critique"] = True
            cur["critique_cap"] = int(m.group(2))
            continue

        # ── Backprop: diverge ──────────────────────────────────────────────
        m = RE_BP_DIVERGE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            cur["diverged"] = True
            cur["n_sel_only"] = int(m.group(2))
            continue

        # ── Backprop done — apply all updates for this iteration ───────────
        m = RE_BP_DONE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            _apply_backprop(root, cur)
            total_iters = int(m.group(1)) + 1
            # Sanity check: root.visits should match log
            expected_root_visits = int(m.group(4))
            if root.visits != expected_root_visits:
                # Mismatch — force-correct root visits (accumulation error)
                pass  # keep going; minor drift is acceptable
            cur = _reset()
            continue

        # ── Search complete ────────────────────────────────────────────────
        m = RE_COMPLETE.search(line) or RE_COMPLETE2.search(line)
        if m:
            bs = float(m.group(1))
            if bs > best_score:
                best_score = bs

    return root, best_score, total_iters


# ---------------------------------------------------------------------------
# Apply one iteration's backpropagation to the tree
# ---------------------------------------------------------------------------

def _apply_backprop(root: ReconNode, cur: dict) -> None:
    rollout   = cur["rollout_history"] or []
    llm_plan  = cur["llm_plan"] or rollout   # default: no divergence
    pre_score = cur["pre_score"]
    crit_plan = cur["critique_plan"] or []
    crit_cap  = cur["critique_cap"]
    crit_score = cur["critique_score"]
    diverged  = cur["diverged"]
    n_sel_only = cur["n_sel_only"]
    has_crit  = cur["has_critique"]

    expanded_depth = len(rollout)

    # ── Resolve sim_backprop_path ──────────────────────────────────────────
    if diverged and llm_plan and expanded_depth > 0:
        truncated_sim = llm_plan[:expanded_depth]
        sim_path = find_or_create_path(root, truncated_sim)
    else:
        # No divergence: sim path == selection path == rollout
        sim_path = find_or_create_path(root, rollout)

    # ── Pass 1: update sim path with pre-critique score ────────────────────
    for node in sim_path:
        node.visits += 1
        node.total_reward += pre_score
        if pre_score > node.best:
            node.best = pre_score

    # ── Virtual visits for selection-only nodes (when diverged) ────────────
    # The log says exactly how many got virtual visits (n_sel_only).
    # These are nodes on the original selection path (rollout ops) NOT in sim_path.
    if diverged and n_sel_only > 0:
        selection_path = find_or_create_path(root, rollout)
        sim_ids = {id(n) for n in sim_path}
        sel_only = [n for n in selection_path if id(n) not in sim_ids]
        for node in sel_only[:n_sel_only]:  # cap to logged count
            node.visits += 1
            # total_reward += 0.0 — no quality signal

    # ── Pass 2: update critique path with critique score ───────────────────
    if has_crit and crit_plan and crit_cap > 0:
        truncated_crit = crit_plan[:crit_cap]
        crit_path = find_or_create_path(root, truncated_crit)
        for node in crit_path:
            node.visits += 1
            node.total_reward += crit_score
            if crit_score > node.best:
                node.best = crit_score


# ---------------------------------------------------------------------------
# Greedy path analysis (same logic as replay_mcts_best_path.py)
# ---------------------------------------------------------------------------

def _key_fn(utility: str):
    if utility == "total_reward":
        return lambda c: (c.total_reward, c.visits)
    elif utility == "best":
        return lambda c: (c.best, c.visits)
    else:
        return lambda c: (c.q, c.visits)


def greedy_path(root: ReconNode, utility: str = "total_reward") -> list:
    path = [root]
    node = root
    key = _key_fn(utility)
    while node.children:
        node = max(node.children.values(), key=key)
        path.append(node)
    return path


def best_on_path(path: list) -> tuple:
    best_node = max(path, key=lambda n: (n.best, n.visits))
    return best_node.best, best_node


# ---------------------------------------------------------------------------
# Per-case analysis
# ---------------------------------------------------------------------------

def _path_stats(path: list, label: str) -> dict:
    leaf = path[-1]
    bop_score, _ = best_on_path(path)
    op_seq = [n.cfg[:60] for n in path[1:]]
    return {
        f"{label}_depth":        len(path) - 1,
        f"{label}_leaf_tr":      round(leaf.total_reward, 4),
        f"{label}_leaf_q":       round(leaf.q, 4),
        f"{label}_leaf_best":    round(leaf.best, 4),
        f"{label}_leaf_visits":  leaf.visits,
        f"{label}_leaf_correct": leaf.best >= 0.9,
        f"{label}_bop_best":     round(bop_score, 4),
        f"{label}_bop_correct":  bop_score >= 0.9,
        f"{label}_op_seq":       " → ".join(op_seq),
    }


def analyse_case_from_log(case_dir: Path) -> list:
    """Analyse one case directory using log files. Returns list of result dicts."""
    log_files = sorted(case_dir.glob("*.log"))
    if not log_files:
        return []

    results = []
    for lf in log_files:
        # Case id: infer from filename (e.g. 1_target5_MCTS_... → case_id = 1_5)
        # Also try tree_viz or action_trace name if present for consistency
        fname = lf.stem  # e.g. "1_target96_MCTS_20260630_150954"
        m = re.match(r'(\d+)_target(\d+)_', fname)
        if m:
            case_id = f"{m.group(1)}_{m.group(2)}"
        else:
            case_id = fname  # fallback

        root, best_score, total_iters = parse_log(lf)
        if root is None or total_iters == 0:
            continue

        # Check if tree has meaningful structure (at least one child with visits)
        if not root.children:
            continue

        path_tr   = greedy_path(root, utility="total_reward")
        path_q    = greedy_path(root, utility="q")
        path_best = greedy_path(root, utility="best")

        result = {
            "case_dir":      case_dir.name,
            "case_id":       case_id,
            "es_iters":      total_iters,
            "es_best_score": round(best_score, 4),
            "es_correct":    best_score >= 0.9,
            "root_visits":   root.visits,
            "root_tr":       round(root.total_reward, 4),
            "root_best":     round(root.best, 4),
        }
        result.update(_path_stats(path_tr,   "tr"))
        result.update(_path_stats(path_q,    "gq"))
        result.update(_path_stats(path_best, "gb"))
        results.append(result)

    return results


# ---------------------------------------------------------------------------
# Length extraction (same as replay_mcts_best_path.py)
# ---------------------------------------------------------------------------

def extract_length_from_id(case_id: str) -> str:
    m = re.match(r'^(\d+)_', case_id)
    return f"l{m.group(1)}" if m else "other"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _pct(n, total):
    return f"{n:3d} / {total} = {n/total:.1%}"


def main():
    parser = argparse.ArgumentParser(
        description="Reconstruct MCTS tree from log files and run greedy-path analysis."
    )
    parser.add_argument(
        "--log_dir",
        default="logs_langraph/rag_det_score_run8_l1_training",
        help="Root log directory",
    )
    parser.add_argument(
        "--no_filter", action="store_true",
        help="Include all case subdirectories (skip canonical cases_lN_pM filter)",
    )
    parser.add_argument(
        "--min_iters", type=int, default=1,
        help="Skip cases with fewer total iterations",
    )
    parser.add_argument(
        "--output", default="mcts_log_replay_results.csv",
        help="Output CSV filename",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    log_dir = Path(args.log_dir)
    if not log_dir.exists():
        print(f"[ERROR] Log directory not found: {log_dir}")
        return

    CANONICAL_RE = re.compile(r'^cases_l\d+_p\d+$')
    case_dirs = sorted(
        d for d in log_dir.iterdir()
        if d.is_dir() and (args.no_filter or CANONICAL_RE.match(d.name))
    )
    print(f"Found {len(case_dirs)} case directories in {log_dir}")

    all_results = []
    skipped_no_log = 0
    skipped_few_iters = 0

    for case_dir in case_dirs:
        case_results = analyse_case_from_log(case_dir)
        if not case_results:
            skipped_no_log += 1
            continue
        for r in case_results:
            if (r["es_iters"] or 0) < args.min_iters:
                skipped_few_iters += 1
                continue
            r["length"] = extract_length_from_id(r["case_id"])
            all_results.append(r)
            if args.verbose:
                es_tag  = "✓" if r["es_correct"]         else "✗"
                tr_tag  = "✓" if r["tr_leaf_correct"]    else "✗"
                bop_tag = "✓" if r["tr_bop_correct"]     else "✗"
                print(
                    f"  {r['case_id']:10s}  "
                    f"es={es_tag}({r['es_iters']}i,{r['es_best_score']:.2f})  "
                    f"root_visits={r['root_visits']:3d}  "
                    f"TR_leaf={tr_tag}(best={r['tr_leaf_best']:.3f})  "
                    f"BOP={bop_tag}({r['tr_bop_best']:.3f})"
                )

    if not all_results:
        print("No results to report.")
        return

    n = len(all_results)

    def cnt(pred):
        return sum(1 for r in all_results if pred(r))

    es_ok  = cnt(lambda r: r["es_correct"])
    tr_ok  = cnt(lambda r: r["tr_leaf_correct"])
    tr_bop = cnt(lambda r: r["tr_bop_correct"])
    gq_ok  = cnt(lambda r: r["gq_leaf_correct"])
    gq_bop = cnt(lambda r: r["gq_bop_correct"])
    gb_ok  = cnt(lambda r: r["gb_leaf_correct"])

    both        = cnt(lambda r: r["es_correct"] and r["tr_leaf_correct"])
    es_only     = cnt(lambda r: r["es_correct"] and not r["tr_leaf_correct"])
    irred       = cnt(lambda r: r["es_correct"] and not r["tr_bop_correct"])
    tr_only     = cnt(lambda r: not r["es_correct"] and r["tr_leaf_correct"])
    neither     = cnt(lambda r: not r["es_correct"] and not r["tr_leaf_correct"])

    W = 65
    print(f"\n{'='*W}")
    print(f"MCTS Log Replay Analysis — {n} cases  (min_iters≥{args.min_iters})")
    print(f"  Source: {log_dir}")
    print(f"{'='*W}")
    print(f"  Skipped (no usable log)  : {skipped_no_log}")
    print(f"  Skipped (few iters)      : {skipped_few_iters}")
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
    print(f"  ES✓ ∧ TR_BOP✗ (still missed)       {irred:3d}  ← irreducible")
    print(f"  ES✗ ∧ TR✓  (TR recovers)            {tr_only:3d}  ← TR wins")
    print(f"  ES✗ ∧ TR✗  (both miss)              {neither:3d}")
    print(f"{'='*W}")

    # ── Per-length breakdown ───────────────────────────────────────────────
    from collections import defaultdict
    by_len = defaultdict(list)
    for r in all_results:
        by_len[r["length"]].append(r)

    if len(by_len) > 1 or list(by_len.keys()) != ["other"]:
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

    # ── Detail: TR leaf misses ─────────────────────────────────────────────
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

    # ── Detail: TR recovers ES misses ──────────────────────────────────────
    if tr_only:
        print(f"\nCases where ES MISSED but TR-leaf recovers ({tr_only}):")
        for r in all_results:
            if not r["es_correct"] and r["tr_leaf_correct"]:
                print(
                    f"  {r['case_id']:10s}  es={r['es_best_score']:.2f}  "
                    f"leaf_best={r['tr_leaf_best']:.3f}"
                )

    # ── CSV output ─────────────────────────────────────────────────────────
    out_path = Path(args.output)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_results[0].keys()))
        writer.writeheader()
        writer.writerows(all_results)
    print(f"\nDetailed results → {out_path}")


if __name__ == "__main__":
    main()
