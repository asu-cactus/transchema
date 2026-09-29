"""
Analyze RAG hit rates by MCTS tree depth.

ONLY RAG-capable call types are counted in hit-rate denominators:
  - MCTS Expand              (always calls get_rag_hints)
  - MCTS Sim Get Next Op     (always calls get_rag_hints)
  - MCTS Simulate            (pipeline mode — always calls get_rag_hints)
  - MCTS Simulate Python     (calls get_rag_hints but template currently broken)

Non-RAG call types (Configure Join/Union/GroupBy, Critique) are reported as
reference counts only — they never produce "--- Example 1 (case" in their prompt.

Depth anchor: [MCTS Select] Iter N: selected depth=D
  All calls between two consecutive Select lines share that selected depth.

Note: Expand calls run at actual prefix_depth = selected_depth (correct).
      Sim Get Next Op runs at actual prefix_depth = selected_depth + 1 because
      the simulation starts from the newly-expanded node (one level deeper).
      Despite this offset, all calls within an iteration are bucketed under the
      selected_depth so the table is easy to read.
"""

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

SELECT_RE = re.compile(r"\[MCTS Select\] Iter \d+: selected depth=(\d+)")
QUERY_RE  = re.compile(r"Query of Type\s*:\s*(.+)$")
EX_RE     = re.compile(r"--- Example 1 \(case")

# Calls that DO attempt get_rag_hints → counted in hit-rate denominator
RAG_EXPAND_TYPES = {"MCTS Expand"}
RAG_SIM_TYPES    = {
    "MCTS Simulate",          # pipeline all-in-one
    "MCTS Sim Get Next Op",   # opsim: operator selector
    "MCTS Simulate Python",   # opsim: python codegen (RAG retrieved, template broken)
}

# Calls that do NOT attempt get_rag_hints → reported as reference counts only
NO_RAG_SIM_TYPES = {
    "MCTS Sim Configure Join",
    "MCTS Sim Configure Union",
    "MCTS Sim Configure GroupBy",
}
CRITIQUE_TYPES = {"MCTS Critique"}


def empty_counts():
    return {
        "exp":      0, "exp_rag":  0,   # expand
        "sim":      0, "sim_rag":  0,   # RAG-capable sim only
        "cfg":      0,                  # configure (non-RAG), reference
        "crit":     0,                  # critique (non-RAG), reference
    }


def parse_log(path: Path) -> dict:
    stats     = defaultdict(empty_counts)
    cur_depth = None
    cur_cat   = None   # "exp" / "sim" / "cfg" / "crit"
    rag_seen  = False

    for line in open(path, encoding="utf-8", errors="replace"):
        if m := SELECT_RE.search(line):
            cur_depth = int(m.group(1))
            continue

        if m := QUERY_RE.search(line):
            qt = m.group(1).strip()
            rag_seen = False

            if qt in RAG_EXPAND_TYPES:
                cur_cat = "exp"
                if cur_depth is not None:
                    stats[cur_depth]["exp"] += 1
            elif qt in RAG_SIM_TYPES:
                cur_cat = "sim"
                if cur_depth is not None:
                    stats[cur_depth]["sim"] += 1
            elif qt in NO_RAG_SIM_TYPES:
                cur_cat = "cfg"
                if cur_depth is not None:
                    stats[cur_depth]["cfg"] += 1
            elif qt in CRITIQUE_TYPES:
                cur_cat = "crit"
                if cur_depth is not None:
                    stats[cur_depth]["crit"] += 1
            else:
                cur_cat = None
            continue

        # RAG example marker — only count for RAG-capable types
        if cur_cat in ("exp", "sim") and not rag_seen and EX_RE.search(line):
            rag_seen = True
            if cur_depth is not None:
                stats[cur_depth][cur_cat + "_rag"] += 1

    return dict(stats)


def aggregate(records: list[dict]) -> dict:
    agg = defaultdict(empty_counts)
    for r in records:
        for depth, counts in r.items():
            for k, v in counts.items():
                agg[depth][k] += v
    return dict(agg)


def pct(num, denom):
    return f"{100*num/denom:5.1f}%" if denom else "    —"


def print_table(agg: dict, label: str, n_cases: int):
    depths = sorted(agg.keys())
    W = 110

    print(f"\n{'─'*W}")
    print(f"  {label}  ({n_cases} cases)")
    print(f"  NOTE: Only RAG-capable calls (Expand, Sim-GetNextOp, Sim-Pipeline, Sim-Python) in "
          f"hit-rate columns.")
    print(f"  Configure calls (Join/Union/GroupBy) and Critique are shown as reference counts only.")
    print(f"{'─'*W}")

    hdr = (
        f"  {'Depth':>5}  "
        f"{'── EXPAND (RAG-capable) ──':^28}  "
        f"{'────── SIMULATE (RAG-capable only) ──────':^43}  "
        f"{'── REFERENCE ──':^18}"
    )
    sub = (
        f"  {'':>5}  "
        f"{'Calls':>6}  {'w/RAG':>6}  {'Hit%':>7}    "
        f"{'Calls':>6}  {'w/RAG':>6}  {'Hit%':>7}    "
        f"{'TOT RAG':>7}  {'Hit%':>7}    "
        f"{'Cfg':>5}  {'Crit':>5}"
    )
    sep = (
        f"  {'─'*5}  {'─'*6}  {'─'*6}  {'─'*7}    "
        f"{'─'*6}  {'─'*6}  {'─'*7}    "
        f"{'─'*7}  {'─'*7}    "
        f"{'─'*5}  {'─'*5}"
    )
    print(hdr); print(sub); print(sep)

    tot_exp = tot_exp_r = 0
    tot_sim = tot_sim_r = 0
    tot_cfg = tot_crit  = 0

    for d in depths:
        c = agg[d]
        ec, er = c["exp"],  c["exp_rag"]
        sc, sr = c["sim"],  c["sim_rag"]
        cfg    = c["cfg"]
        crit   = c["crit"]
        tc     = ec + sc
        tr     = er + sr
        tot_exp  += ec; tot_exp_r += er
        tot_sim  += sc; tot_sim_r += sr
        tot_cfg  += cfg; tot_crit += crit
        print(
            f"  {d:>5}  "
            f"{ec:>6}  {er:>6}  {pct(er,ec):>7}    "
            f"{sc:>6}  {sr:>6}  {pct(sr,sc):>7}    "
            f"{tc:>7}  {pct(tr,tc):>7}    "
            f"{cfg:>5}  {crit:>5}"
        )

    print(sep)
    tot_c = tot_exp + tot_sim
    tot_r = tot_exp_r + tot_sim_r
    print(
        f"  {'TOT':>5}  "
        f"{tot_exp:>6}  {tot_exp_r:>6}  {pct(tot_exp_r,tot_exp):>7}    "
        f"{tot_sim:>6}  {tot_sim_r:>6}  {pct(tot_sim_r,tot_sim):>7}    "
        f"{tot_c:>7}  {pct(tot_r,tot_c):>7}    "
        f"{tot_cfg:>5}  {tot_crit:>5}"
    )


def main():
    by_exp = {}
    for exp in EXPERIMENT_DIRS:
        exp_path = LOG_BASE / exp
        if not exp_path.exists():
            continue
        by_exp[exp] = [parse_log(lf) for lf in sorted(exp_path.glob("*.log"))]

    opsim_exps    = [e for e in EXPERIMENT_DIRS if e in by_exp and "opsim"    in e]
    pipeline_exps = [e for e in EXPERIMENT_DIRS if e in by_exp and "pipeline" in e]

    print("=" * 110)
    print("RAG HIT RATE BY MCTS SELECTED DEPTH  (RAG-capable calls only)")
    print("  Depth  = 'selected depth' from [MCTS Select] — all calls in an iteration share it.")
    print("  Hit%   = fraction of RAG-capable calls that actually got '--- Example 1 (case' in prompt.")
    print("  Cfg    = Configure Join/Union/GroupBy calls (no RAG in current logs — reference only).")
    print("  Crit   = Critique calls (no RAG in current logs — reference only).")
    print("=" * 110)

    for label, exps in [("Operator-based Simulation (opsim)", opsim_exps),
                        ("Pipeline-based Simulation (pipeline)", pipeline_exps)]:
        records = [r for e in exps for r in by_exp[e]]
        agg = aggregate(records)
        print_table(agg, label, len(records))

    all_records = [r for rs in by_exp.values() for r in rs]
    print_table(aggregate(all_records), "GRAND TOTAL", len(all_records))
    print()


if __name__ == "__main__":
    main()
