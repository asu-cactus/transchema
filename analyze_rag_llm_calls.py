"""
Analyze RAG LLM call statistics across MCTS experiment log directories.
Reports expand / simulate / critique / total counts and RAG coverage.
"""

import os
import re
from collections import defaultdict
from pathlib import Path

LOG_BASE = Path("/home/asurite.ad.asu.edu/jrtandel/transchema/logs_langraph")

EXPERIMENT_DIRS = [
    "mcts_l1_p1_rag_ub_partial_opsim",
    "mcts_l1_p1_rag_ub_partial_pipeline",
    "mcts_l1_p2_rag_ub_partial_opsim",
    "mcts_l1_p2_rag_ub_partial_pipeline",
    "mcts_l4_p1_rag_ub_partial_opsim",
    "mcts_l4_p1_rag_ub_partial_pipeline",
    "mcts_l4_p2_rag_ub_partial_opsim",
    "mcts_l4_p2_rag_ub_partial_pipeline",
    "mcts_l9_p1_rag_ub_partial_opsim",
    "mcts_l9_p1_rag_ub_partial_pipeline",
    "mcts_l9_p2_rag_ub_partial_opsim",
    "mcts_l9_p2_rag_ub_partial_pipeline",
]

# Categorise each query type
EXPAND_TYPES = {"MCTS Expand"}
SIMULATE_TYPES = {
    "MCTS Simulate",              # pipeline all-in-one
    "MCTS Sim Get Next Op",       # opsim: operator selector
    "MCTS Sim Configure Join",    # opsim: join configurator
    "MCTS Sim Configure Union",   # opsim: union configurator
    "MCTS Sim Configure GroupBy", # opsim: group-by configurator
    "MCTS Simulate Python",       # opsim: code generator
}
CRITIQUE_TYPES = {"MCTS Critique"}

# Only these types use RAG (others never have "Example 1 (case" in prompt)
RAG_CAPABLE_TYPES = {"MCTS Expand", "MCTS Simulate", "MCTS Sim Get Next Op"}

QUERY_RE = re.compile(r"Query of Type\s*:\s*(.+)$")
TOTAL_RE = re.compile(r"\[MCTS\] Total queries:\s*(\d+)")
RAG_EX_RE = re.compile(r"--- Example 1 \(case")


def parse_log(path: Path) -> dict:
    """Return per-call stats for a single log file."""
    stats = defaultdict(int)
    current_type = None
    rag_seen_for_current = False

    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            # Check for total queries report
            m = TOTAL_RE.search(line)
            if m:
                stats["total_reported"] = int(m.group(1))
                continue

            # New LLM call
            m = QUERY_RE.search(line)
            if m:
                current_type = m.group(1).strip()
                rag_seen_for_current = False
                stats["total_calls"] += 1

                if current_type in EXPAND_TYPES:
                    stats["expand"] += 1
                elif current_type in SIMULATE_TYPES:
                    stats["simulate"] += 1
                    stats[f"simulate_{current_type.replace(' ', '_')}"] += 1
                elif current_type in CRITIQUE_TYPES:
                    stats["critique"] += 1
                else:
                    stats[f"other_{current_type.replace(' ', '_')}"] += 1
                continue

            # RAG example marker — belongs to the current call
            if current_type and not rag_seen_for_current and RAG_EX_RE.search(line):
                rag_seen_for_current = True
                stats["calls_with_rag"] += 1
                if current_type in EXPAND_TYPES:
                    stats["expand_with_rag"] += 1
                elif current_type in SIMULATE_TYPES:
                    stats["simulate_with_rag"] += 1

    return dict(stats)


def aggregate(records: list[dict]) -> dict:
    """Sum a list of stat dicts."""
    totals = defaultdict(int)
    for r in records:
        for k, v in r.items():
            totals[k] += v
    return dict(totals)


def fmt(stats: dict) -> str:
    expand       = stats.get("expand", 0)
    expand_rag   = stats.get("expand_with_rag", 0)
    simulate     = stats.get("simulate", 0)
    sim_rag      = stats.get("simulate_with_rag", 0)
    critique     = stats.get("critique", 0)
    total        = stats.get("total_calls", 0)
    total_rag    = stats.get("calls_with_rag", 0)
    reported     = stats.get("total_reported", 0)

    # Break down simulate sub-types
    sim_sub = {
        "Simulate (pipeline)":   stats.get("simulate_MCTS_Simulate", 0),
        "Sim Get Next Op":       stats.get("simulate_MCTS_Sim_Get_Next_Op", 0),
        "Sim Cfg Join":          stats.get("simulate_MCTS_Sim_Configure_Join", 0),
        "Sim Cfg Union":         stats.get("simulate_MCTS_Sim_Configure_Union", 0),
        "Sim Cfg GroupBy":       stats.get("simulate_MCTS_Sim_Configure_GroupBy", 0),
        "Simulate Python":       stats.get("simulate_MCTS_Simulate_Python", 0),
    }
    sim_sub_str = "  |  ".join(f"{k}: {v}" for k, v in sim_sub.items() if v > 0)

    rag_pct = f"{100*total_rag/total:.1f}%" if total else "—"
    expand_rag_pct  = f"{100*expand_rag/expand:.1f}%"  if expand  else "—"
    sim_rag_pct     = f"{100*sim_rag/simulate:.1f}%"   if simulate else "—"

    lines = [
        f"  expand   : {expand:4d}   (with RAG: {expand_rag:4d} = {expand_rag_pct})",
        f"  simulate : {simulate:4d}   (with RAG: {sim_rag:4d} = {sim_rag_pct})",
    ]
    if sim_sub_str:
        lines.append(f"    └─ {sim_sub_str}")
    if critique:
        lines.append(f"  critique : {critique:4d}")
    lines.append(f"  total    : {total:4d}   (with RAG: {total_rag:4d} = {rag_pct})")
    if reported:
        lines.append(f"  [reported total from log: {reported}]")
    return "\n".join(lines)


def main():
    # Collect stats per file, grouped by experiment and length
    by_exp   = {}   # exp_dir → {file_name → stats}
    by_length = defaultdict(list)

    for exp in EXPERIMENT_DIRS:
        exp_path = LOG_BASE / exp
        if not exp_path.exists():
            print(f"  [SKIP] {exp} — directory not found")
            continue

        log_files = sorted(exp_path.glob("*.log"))
        file_stats = {}
        for lf in log_files:
            file_stats[lf.name] = parse_log(lf)
        by_exp[exp] = file_stats

        # Extract length from dir name (mcts_lN_...)
        m = re.search(r"mcts_l(\d+)_", exp)
        if m:
            by_length[f"length{m.group(1)}"].append(exp)

    # ── Per-experiment summary ─────────────────────────────────────────────
    print("=" * 70)
    print("PER-EXPERIMENT SUMMARY")
    print("=" * 70)
    for exp in EXPERIMENT_DIRS:
        if exp not in by_exp:
            continue
        records = list(by_exp[exp].values())
        agg = aggregate(records)
        n_cases = len(records)
        print(f"\n[{exp}]  ({n_cases} cases)")
        print(fmt(agg))

    # ── Per-length summary ─────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("PER-LENGTH SUMMARY")
    print("=" * 70)
    length_agg = {}
    for length_key in sorted(by_length.keys()):
        exps = by_length[length_key]
        records_all = []
        for exp in exps:
            if exp in by_exp:
                records_all.extend(by_exp[exp].values())
        agg = aggregate(records_all)
        length_agg[length_key] = agg
        n_cases = len(records_all)
        n_exps  = len(exps)
        print(f"\n[{length_key}]  ({n_exps} experiments, {n_cases} total cases)")
        print(fmt(agg))

    # ── Grand total ────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("GRAND TOTAL (all experiments)")
    print("=" * 70)
    all_records = []
    for exp in by_exp.values():
        all_records.extend(exp.values())
    grand = aggregate(all_records)
    n_total_cases = len(all_records)
    n_total_exps  = len(by_exp)
    print(f"\n[ALL]  ({n_total_exps} experiments, {n_total_cases} total cases)")
    print(fmt(grand))
    print()


if __name__ == "__main__":
    main()
