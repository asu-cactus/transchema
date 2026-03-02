"""viz.py — Post-run MCTS visualization utilities.

Writes two human-readable files to the log directory after each MCTS run:

  action_trace_{case_id}.txt
      Chronological breakdown of every MCTS iteration:
      SELECT → EXPAND → SIMULATE → SCORE → BACKPROP

  tree_viz_{case_id}.txt
      ASCII tree of the final MCTS node tree with visit counts,
      Q-values, and best scores per node.

Called from mcts_search.py after mcts_graph.invoke() completes.
"""

import os
import re
from typing import Any, List

# ─── Regex patterns for parsing log_messages ──────────────────────────────────
_RE_SELECT   = re.compile(r"^Iter (\d+): selected node depth=(\d+) op=(.+)$")
_RE_EXPAND   = re.compile(r"^\[EXPAND\] iter=(\d+) op=(\S+) configured=(.+)$")
_RE_SIMULATE = re.compile(r"^\[SIMULATE\] iter=(\d+) trials=(\d+) result=(.+)$")
_RE_SCORE    = re.compile(r"^Iter (\d+): score=([\d.]+) history=(.+)$")
_RE_BACKPROP = re.compile(r"^Backprop iter (\d+): reward=([\d.]+)$")
_RE_DONE     = re.compile(r"^MCTS complete after (\d+) iterations\. Best score=([\d.]+)$")


# ─────────────────────────────────────────────────────────────────────────────
# File 1: Action trace
# ─────────────────────────────────────────────────────────────────────────────

def write_action_trace(
    log_messages: List[str],
    case_id: str,
    out_dir: str,
    best_score: float,
    best_history: List[str],
) -> str:
    """
    Parse log_messages and write a per-iteration action trace.

    Parameters
    ----------
    log_messages  : accumulated log_messages list from MCTSGraphState
    case_id       : e.g. "2_5"
    out_dir       : directory to write the file into
    best_score    : final best score across all iterations
    best_history  : final best operation_history list

    Returns
    -------
    str — path of the written file
    """
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"action_trace_{case_id}.txt")

    # ── Parse messages into per-iteration buckets ──────────────────────────
    iters: dict = {}
    summary: dict = {}

    for msg in log_messages:
        m = _RE_SELECT.match(msg)
        if m:
            it = int(m.group(1))
            iters.setdefault(it, {})["select"] = {
                "depth": int(m.group(2)), "op": m.group(3)
            }
            continue

        m = _RE_EXPAND.match(msg)
        if m:
            it = int(m.group(1))
            iters.setdefault(it, {})["expand"] = {
                "op": m.group(2), "configured": m.group(3)
            }
            continue

        m = _RE_SIMULATE.match(msg)
        if m:
            it = int(m.group(1))
            iters.setdefault(it, {})["simulate"] = {
                "trials": int(m.group(2)), "result": m.group(3)
            }
            continue

        m = _RE_SCORE.match(msg)
        if m:
            it = int(m.group(1))
            iters.setdefault(it, {})["score"] = {
                "score": float(m.group(2)), "history": m.group(3)
            }
            continue

        m = _RE_BACKPROP.match(msg)
        if m:
            it = int(m.group(1))
            iters.setdefault(it, {})["backprop"] = {"reward": float(m.group(2))}
            continue

        m = _RE_DONE.match(msg)
        if m:
            summary = {"total": int(m.group(1)), "best_score": float(m.group(2))}

    # ── Format output ──────────────────────────────────────────────────────
    lines: List[str] = [
        f"MCTS Action Trace — case {case_id}",
        "=" * 60,
        "",
    ]

    running_best = 0.0
    for it in sorted(iters):
        ev = iters[it]
        dash_count = max(0, 47 - len(str(it)))
        lines.append(f"── Iteration {it} " + "─" * dash_count)

        # SELECT
        if "select" in ev:
            s = ev["select"]
            lines.append(f"  SELECT    depth={s['depth']}  parent_op={s['op']}")

        # EXPAND
        if "expand" in ev:
            e = ev["expand"]
            lines.append(f"  EXPAND    op={e['op']}")
            lines.append(f"            → {e['configured']}")
        else:
            lines.append("  EXPAND    (skipped — terminal re-simulation)")

        # SIMULATE
        if "simulate" in ev:
            sim = ev["simulate"]
            ok = sim["result"] == "Success"
            icon = "✓" if ok else "✗"
            lines.append(
                f"  SIMULATE  {icon} {sim['result']}"
                f"  (trials used: {sim['trials']})"
            )

        # SCORE
        if "score" in ev:
            sc = ev["score"]
            new_best = sc["score"] > running_best
            tag = "  ★ NEW BEST" if new_best else ""
            if new_best:
                running_best = sc["score"]
            lines.append(f"  SCORE     {sc['score']:.4f}{tag}")
            lines.append(f"            history: {sc['history']}")

        # BACKPROP
        if "backprop" in ev:
            lines.append(f"  BACKPROP  reward={ev['backprop']['reward']:.4f}")

        lines.append("")

    lines += [
        "=" * 60,
        "SUMMARY",
        f"  Total iterations : {summary.get('total', len(iters))}",
        f"  Best score       : {best_score:.4f}",
        f"  Best history     : {best_history}",
        "",
    ]

    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# File 2: Tree visualization
# ─────────────────────────────────────────────────────────────────────────────

def write_tree_viz(
    root: Any,
    case_id: str,
    out_dir: str,
    best_history: List[str],
) -> str:
    """
    Write an ASCII tree of the final MCTS node tree.

    Parameters
    ----------
    root          : MCTSNode — root of the search tree
    case_id       : e.g. "2_5"
    out_dir       : directory to write the file into
    best_history  : final best operation_history list (used to mark best path)

    Returns
    -------
    str — path of the written file
    """
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"tree_viz_{case_id}.txt")

    lines: List[str] = [
        f"MCTS Tree Visualization — case {case_id}",
        "=" * 60,
        "",
    ]

    def _render(node: Any, prefix: str, is_last: bool, depth: int) -> None:
        oh = node.operation_history

        # Best-path tagging
        if oh == best_history and len(oh) > 0:
            path_tag = "  ★ BEST RESULT"
        elif len(oh) > 0 and best_history[:len(oh)] == oh:
            path_tag = "  · best path"
        else:
            path_tag = ""

        terminal_tag = "  [TERMINAL]" if node.is_terminal else ""
        label = node.operator_type if node.operator_type is not None else "ROOT"

        stats = (
            f"visits={node.visits:3d}  "
            f"q={node.q_value:.3f}  "
            f"best={node.best_score:.3f}"
            f"{terminal_tag}{path_tag}"
        )

        child_prefix = prefix + ("    " if is_last else "│   ")

        if depth == 0:
            lines.append(f"[ROOT]  {stats}")
        else:
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{label:<25s}  {stats}")
            # Show full configured step (last element of operation_history).
            # Skipped when it equals operator_type (e.g. NO_MORE_OPERATION adds no info).
            cfg = node.operation_history[-1] if node.operation_history else ""
            if cfg and cfg != label:
                display_cfg = cfg if len(cfg) <= 120 else cfg[:117] + "..."
                lines.append(f"{child_prefix}    {display_cfg}")
        children = list(node.children.values())
        for i, child in enumerate(children):
            _render(child, child_prefix, i == len(children) - 1, depth + 1)

    _render(root, "", True, 0)

    lines += [
        "",
        "Legend",
        "  visits  number of simulations that passed through this node",
        "  q       average reward (total_reward / visits)",
        "  best    highest single reward seen from any simulation through this node",
        "  ·       on the path to the best result",
        "  ★       the node whose simulation produced the best overall result",
        "",
    ]

    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    return out_path
