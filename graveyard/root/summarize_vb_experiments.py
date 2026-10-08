"""
Summarize VB-score experiments across all lengths.

Methods:
  COO                      — multistep only (no critique)
  COO+Critique             — multistep + critique (accuracy from critique if invoked)
  COT                      — single-step COT only (no critique)
  COT+Critique             — single-step COT + critique
  COO+Materialization      — multistep + materialization + critique
  MCTS Operator            — MCTS operator simulation
  MCTS Pipeline            — MCTS pipeline simulation
"""

import json, os, glob
import pandas as pd
from collections import defaultdict

BASE    = os.path.dirname(os.path.abspath(__file__))
LENGTHS = [1, 2, 3, 4, 5, 6, 9]


# ─── Critique experiment helpers ─────────────────────────────────────────────

def find_json_dirs(length: int, name_fragment: str) -> list[str]:
    """Return all jsons/ subdirs under lenN_vb_iter1_no_budget whose parent
    dir name contains name_fragment (handles resume / p1 / p2 variants)."""
    log_root = os.path.join(BASE, f"len{length}_vb_iter1_no_budget")
    if not os.path.isdir(log_root):
        return []
    dirs = []
    for d in sorted(os.listdir(log_root)):
        if name_fragment in d:
            jsons = os.path.join(log_root, d, "jsons")
            if os.path.isdir(jsons):
                dirs.append(jsons)
    return dirs


def load_cases(dirs: list[str]) -> dict:
    """Load JSON case files from all dirs; last write wins on duplicate case_id."""
    cases = {}
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d, "*.json"))):
            case_id = os.path.splitext(os.path.basename(f))[0]
            try:
                with open(f) as fh:
                    cases[case_id] = json.load(fh)
            except Exception:
                pass
    return cases


def metrics_from_cases(cases: dict, include_critique: bool) -> dict | None:
    """
    include_critique=False  → COO / COT  (ms metrics only, critiques ignored)
    include_critique=True   → COO+Critique / COT+Critique / COO+Mat+Crit
        - If critique was invoked: accuracy = last critique is_correct,
                                   cost/latency = ms + all critiques
        - If critique was NOT invoked (score already >= 0.9):
                                   accuracy = ms.is_correct,
                                   cost/latency = ms only
    """
    if not cases:
        return None

    acc_list, cost_list, lat_list = [], [], []

    for data in cases.values():
        iters = data.get("iterations", [])
        if not iters:
            continue
        it       = iters[0]
        ms       = it.get("ms", {})
        critiques = it.get("critiques", [])

        ms_correct  = bool(ms.get("is_correct", False))
        ms_cost     = float(ms.get("cost", 0.0))
        ms_latency  = float(ms.get("latency", 0.0))

        if not include_critique or not critiques:
            acc_list.append(1 if ms_correct else 0)
            cost_list.append(ms_cost)
            lat_list.append(ms_latency)
        else:
            crit_cost    = sum(float(c.get("cost", 0.0))    for c in critiques)
            crit_latency = sum(float(c.get("latency", 0.0)) for c in critiques)
            crit_correct = bool(critiques[-1].get("is_correct", False))
            acc_list.append(1 if crit_correct else 0)
            cost_list.append(ms_cost    + crit_cost)
            lat_list.append(ms_latency  + crit_latency)

    if not acc_list:
        return None

    n = len(acc_list)
    return {
        "n":           n,
        "accuracy":    sum(acc_list),
        "avg_cost":    sum(cost_list) / n,
        "avg_latency": sum(lat_list)  / n,
    }


# ─── MCTS helpers ─────────────────────────────────────────────────────────────

def load_mcts_cases(length: int, sim: str) -> dict:
    """Load MCTS results_summary.csv for a given length and simulation mode."""
    mcts_root = os.path.join(BASE, "Langraph", "results_langraph")
    if not os.path.isdir(mcts_root):
        return {}
    cases = {}
    tag = f"len{length}_vb_mcts_{sim}"
    for d in sorted(os.listdir(mcts_root)):
        if tag in d:
            csv_path = os.path.join(mcts_root, d, "results_summary.csv")
            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path)
                    for _, row in df.iterrows():
                        cid = str(row["case_id"])
                        cases[cid] = row.to_dict()
                except Exception:
                    pass
    return cases


def metrics_from_mcts(cases: dict) -> dict | None:
    if not cases:
        return None
    acc_list, cost_list, lat_list = [], [], []
    for row in cases.values():
        is_correct = str(row.get("is_correct", "False")).strip().lower() == "true"
        acc_list.append(1 if is_correct else 0)
        cost_val = row.get("cost", 0.0)
        lat_val  = row.get("latency_seconds", 0.0)
        cost_list.append(float(cost_val) if pd.notna(cost_val) else 0.0)
        lat_list.append(float(lat_val)   if pd.notna(lat_val)  else 0.0)
    n = len(acc_list)
    return {
        "n":           n,
        "accuracy":    sum(acc_list),
        "avg_cost":    sum(cost_list) / n,
        "avg_latency": sum(lat_list)  / n,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def fmt(m: dict | None) -> tuple:
    if m is None:
        return ("—", "—", "—", "—")
    return (
        m["n"],
        m["accuracy"],
        f"{m['avg_latency']:.2f}s",
        f"${m['avg_cost']:.5f}",
    )


METHODS = [
    ("COO",                      "multistep_critique",  False),
    ("COO+Critique",             "multistep_critique",  True),
    ("COT",                      "sscot_critique",      False),
    ("COT+Critique",             "sscot_critique",      True),
    ("COO+Materialization+Crit", "ms_materialization",  True),
]

rows = []

for length in LENGTHS:
    for method_name, fragment, with_crit in METHODS:
        dirs  = find_json_dirs(length, fragment)
        cases = load_cases(dirs)
        m     = metrics_from_cases(cases, with_crit)
        n, acc, lat, cost = fmt(m)
        rows.append({
            "Length": f"len{length}",
            "Method": method_name,
            "N": n,
            "Accuracy": acc,
            "Avg Latency": lat,
            "Avg Cost": cost,
        })

    # MCTS
    for sim_label, sim_key in [("MCTS Operator", "op"), ("MCTS Pipeline", "pl")]:
        cases = load_mcts_cases(length, sim_key)
        m     = metrics_from_mcts(cases)
        n, acc, lat, cost = fmt(m)
        rows.append({
            "Length": f"len{length}",
            "Method": sim_label,
            "N": n,
            "Accuracy": acc,
            "Avg Latency": lat,
            "Avg Cost": cost,
        })

df = pd.DataFrame(rows)

# ── Print per-length tables ──────────────────────────────────────────────────
for length in LENGTHS:
    sub = df[df["Length"] == f"len{length}"].drop(columns="Length")
    print(f"\n{'='*65}")
    print(f"  Length {length}")
    print(f"{'='*65}")
    print(sub.to_string(index=False))

# ── Print aggregated (all lengths combined) ──────────────────────────────────
print(f"\n{'='*65}")
print("  AGGREGATE (all lengths)")
print(f"{'='*65}")

agg_rows = []
for method_name, fragment, with_crit in METHODS:
    all_cases = {}
    for length in LENGTHS:
        dirs  = find_json_dirs(length, fragment)
        all_cases.update(load_cases(dirs))
    m = metrics_from_cases(all_cases, with_crit)
    n, acc, lat, cost = fmt(m)
    agg_rows.append({"Method": method_name, "N": n, "Accuracy": acc,
                     "Avg Latency": lat, "Avg Cost": cost})

for sim_label, sim_key in [("MCTS Operator", "op"), ("MCTS Pipeline", "pl")]:
    all_cases = {}
    for length in LENGTHS:
        all_cases.update(load_mcts_cases(length, sim_key))
    m = metrics_from_mcts(all_cases)
    n, acc, lat, cost = fmt(m)
    agg_rows.append({"Method": sim_label, "N": n, "Accuracy": acc,
                     "Avg Latency": lat, "Avg Cost": cost})

print(pd.DataFrame(agg_rows).to_string(index=False))
