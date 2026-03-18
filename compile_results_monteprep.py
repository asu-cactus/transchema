"""
compile_results_monteprep.py — MontePrep experiment result compiler

Outputs: results_analysis_monteprep.xlsx with sheets:
  1. Overall     — accuracy, avg cost, avg latency per experiment x model
  2. L1          — per-case is_correct for each experiment
  3. L4          — per-case is_correct for each experiment
  4. L9          — per-case is_correct for each experiment
  5. Remaining   — completion status per experiment
  6. Sources     — result CSV paths used

Run from: ~/transchema/
  python3 compile_results_monteprep.py
"""

import os
import pandas as pd
from pathlib import Path

ROOT      = Path(__file__).resolve().parent
AF_DIRS   = ROOT / "AgentFlow" / "results"
MS_BASE   = ROOT / "logs-auto-suggest-llm-21-04"
MCTS_DIRS = ROOT / "Langraph" / "results_langraph"
OUT       = ROOT / "results_analysis_monteprep.xlsx"

# Expected case counts per length for monteprep
EXPECTED = {1: set(range(0, 100)), 4: set(range(0, 80)), 9: set(range(0, 30))}


# ── Helpers ───────────────────────────────────────────────────────────────────

def concat_csvs(paths):
    dfs = []
    for p in paths:
        p = Path(p)
        if p.exists():
            try:
                df = pd.read_csv(p)
                if not df.empty:
                    dfs.append(df)
            except Exception as e:
                print(f"  WARNING: could not read {p}: {e}")
        else:
            print(f"  WARNING: not found: {p}")
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def extract_len(case_id):
    try:
        return int(str(case_id).split("_")[0])
    except Exception:
        return None


# ── Loaders ───────────────────────────────────────────────────────────────────

def load_agentflow(exp_dirs):
    paths = [AF_DIRS / d / "results_summary.csv" for d in exp_dirs]
    df = concat_csvs(paths)
    if df.empty:
        return df
    df["case_id"] = df["case_id"].astype(str)
    df["len"] = df["case_id"].apply(extract_len)
    df["is_correct"] = df["is_correct"].map(
        lambda v: True if str(v).strip().lower() in ("true", "1") else False
    )
    df["cost"]            = pd.to_numeric(df.get("cost"),            errors="coerce").fillna(0)
    df["latency_seconds"] = pd.to_numeric(df.get("latency_seconds"), errors="coerce").fillna(0)
    return df[["case_id", "len", "is_correct", "cost", "latency_seconds"]]


def load_mcts(exp_dirs):
    paths = [MCTS_DIRS / d / "results_summary.csv" for d in exp_dirs]
    df = concat_csvs(paths)
    if df.empty:
        return df
    df["case_id"] = df["case_id"].astype(str)
    df["len"] = df["case_id"].apply(extract_len)
    df["is_correct"] = df["is_correct"].map(
        lambda v: True if str(v).strip().lower() in ("true", "1") else False
    )
    df["cost"]            = pd.to_numeric(df.get("cost"),            errors="coerce").fillna(0)
    df["latency_seconds"] = pd.to_numeric(df.get("latency_seconds"), errors="coerce").fillna(0)
    return df[["case_id", "len", "is_correct", "cost", "latency_seconds"]]


def load_sscot(exp_dirs):
    """Load SSCoT results (multi_step.csv = pass-1, critique.csv = pass-2 combined)."""
    ms_paths   = [MS_BASE / d / "results" / "multi_step.csv" for d in exp_dirs]
    crit_paths = [MS_BASE / d / "results" / "critique.csv"   for d in exp_dirs]

    ms_df = concat_csvs(ms_paths)
    if ms_df.empty:
        return pd.DataFrame()

    ms_df = ms_df.rename(columns={
        "Length":     "case_id",
        "Hard Match": "ms_correct",
        "Soft Match": "cost",
        "Soft Acc":   "latency_seconds",
    })
    ms_df["case_id"]         = ms_df["case_id"].astype(str)
    ms_df["ms_correct"]      = ms_df["ms_correct"].map(
        lambda v: True if str(v).strip().lower() in ("true", "1") else False
    )
    ms_df["cost"]            = pd.to_numeric(ms_df["cost"],            errors="coerce").fillna(0)
    ms_df["latency_seconds"] = pd.to_numeric(ms_df["latency_seconds"], errors="coerce").fillna(0)

    crit_df = concat_csvs(crit_paths)
    if not crit_df.empty:
        crit_df = crit_df.rename(columns={
            "Length":     "case_id",
            "Hard Match": "crit_correct",
            "Soft Match": "crit_cost",
            "Soft Acc":   "crit_latency",
        })
        crit_df["case_id"]      = crit_df["case_id"].astype(str)
        crit_df["crit_correct"] = crit_df["crit_correct"].map(
            lambda v: True if str(v).strip().lower() in ("true", "1") else False
        )
        crit_df["crit_cost"]    = pd.to_numeric(crit_df.get("crit_cost"),    errors="coerce").fillna(0)
        crit_df["crit_latency"] = pd.to_numeric(crit_df.get("crit_latency"), errors="coerce").fillna(0)
        crit_best = (
            crit_df.groupby("case_id")
            .agg(crit_correct=("crit_correct", "any"),
                 crit_cost=("crit_cost", "sum"),
                 crit_latency=("crit_latency", "sum"))
            .reset_index()
        )
        ms_df = ms_df.merge(crit_best, on="case_id", how="left")
        ms_df["crit_correct"] = ms_df["crit_correct"].fillna(False)
        ms_df["crit_cost"]    = ms_df["crit_cost"].fillna(0)
        ms_df["crit_latency"] = ms_df["crit_latency"].fillna(0)
    else:
        ms_df["crit_correct"] = False
        ms_df["crit_cost"]    = 0
        ms_df["crit_latency"] = 0

    ms_df["is_correct"]      = ms_df["ms_correct"] | ms_df["crit_correct"]
    ms_df["cost"]            += ms_df["crit_cost"]
    ms_df["latency_seconds"] += ms_df["crit_latency"]
    ms_df["len"]              = ms_df["case_id"].apply(extract_len)
    return ms_df[["case_id", "len", "is_correct", "cost", "latency_seconds"]]


# ── Load all experiments ───────────────────────────────────────────────────────

# SSCoT — gpt-4.1-mini
sscot_41mini_l1 = load_sscot(["mp_l1_41mini_sscot_0_99_20260317_174300"])
sscot_41mini_l4 = load_sscot(["mp_l4_41mini_sscot_0_79_20260317_174329"])
sscot_41mini_l9 = load_sscot(["mp_l9_41mini_sscot_0_29_20260317_174348"])
print(f"SSCoT 4.1-mini  L1: {len(sscot_41mini_l1)} | L4: {len(sscot_41mini_l4)} | L9: {len(sscot_41mini_l9)}")

# SSCoT — o4-mini (original 0-99 + reruns for 66-89 and 90-99, later runs take precedence)
sscot_o4mini_l1 = load_sscot([
    "mp_l1_o4mini_sscot_0_99_20260317_174408",
    "mp_l1_o4mini_sscot_66_99_20260318_131752",
    "mp_l1_o4mini_sscot_90_99_20260318_134324",
]).drop_duplicates(subset="case_id", keep="last")
sscot_o4mini_l4 = load_sscot(["mp_l4_o4mini_sscot_0_79_20260317_174516"])
sscot_o4mini_l9 = load_sscot(["mp_l9_o4mini_sscot_0_29_20260317_174540"])
print(f"SSCoT o4-mini   L1: {len(sscot_o4mini_l1)} | L4: {len(sscot_o4mini_l4)} | L9: {len(sscot_o4mini_l9)}")

# AgentFlow Operator — gpt-4.1-mini
af_op_41mini_l1 = load_agentflow([
    "mp_l1_41mini_af_op_0_49_20260317_230408",
    "mp_l1_41mini_af_op_50_99_20260317_230408",
])
af_op_41mini_l4 = load_agentflow([])   # blocked — not started yet
af_op_41mini_l9 = load_agentflow([
    "mp_l9_41mini_af_op_0_14_20260317_183500",
    "mp_l9_41mini_af_op_15_29_20260317_183500",
])
print(f"AF Op 4.1-mini  L1: {len(af_op_41mini_l1)} | L4: {len(af_op_41mini_l4)} | L9: {len(af_op_41mini_l9)}")

# AgentFlow Operator — o4-mini
af_op_o4mini_l1 = load_agentflow([
    "mp_l1_o4mini_af_op_0_49_20260317_222618",
    "mp_l1_o4mini_af_op_50_99_20260317_222618",
])
af_op_o4mini_l4 = load_agentflow([
    "mp_l4_o4mini_af_op_0_39_20260318_103556",
    "mp_l4_o4mini_af_op_40_79_20260318_103556",
])
af_op_o4mini_l9 = load_agentflow([
    "mp_l9_o4mini_af_op_0_14_20260317_182940",
    "mp_l9_o4mini_af_op_15_29_20260317_182940",
])
print(f"AF Op o4-mini   L1: {len(af_op_o4mini_l1)} | L4: {len(af_op_o4mini_l4)} | L9: {len(af_op_o4mini_l9)}")

# AgentFlow Pipeline — gpt-4.1-mini
af_pl_41mini_l1 = load_agentflow([
    "mp_l1_41mini_af_pl_0_49_20260318_002718",
    "mp_l1_41mini_af_pl_50_99_20260318_002718",
])
af_pl_41mini_l4 = load_agentflow([])   # blocked — not started yet
af_pl_41mini_l9 = load_agentflow([
    "mp_l9_41mini_af_pl_0_14_20260317_193251",
    "mp_l9_41mini_af_pl_15_29_20260317_193251",
])
print(f"AF Pl 4.1-mini  L1: {len(af_pl_41mini_l1)} | L4: {len(af_pl_41mini_l4)} | L9: {len(af_pl_41mini_l9)}")

# AgentFlow Pipeline — o4-mini
af_pl_o4mini_l1 = load_agentflow([
    "mp_l1_o4mini_af_pl_0_49_20260318_020649",
    "mp_l1_o4mini_af_pl_50_99_20260318_020649",
])
af_pl_o4mini_l4 = load_agentflow([])   # not started yet
af_pl_o4mini_l9 = load_agentflow([
    "mp_l9_o4mini_af_pl_0_14_20260317_195201",
    "mp_l9_o4mini_af_pl_15_29_20260317_195201",
])
print(f"AF Pl o4-mini   L1: {len(af_pl_o4mini_l1)} | L4: {len(af_pl_o4mini_l4)} | L9: {len(af_pl_o4mini_l9)}")

# MCTS — gpt-4.1-mini
mcts_41mini_l1 = load_mcts([
    "mp_l1_41mini_mcts_0_49_20260318_012435",
    "mp_l1_41mini_mcts_50_99_20260318_012435",
    "mp_l1_41mini_mcts_89_99_20260318_121428",
])
mcts_41mini_l4 = load_mcts([])   # blocked — not started yet
mcts_41mini_l9 = load_mcts([
    "mp_l9_41mini_mcts_0_14_20260317_203957",
    "mp_l9_41mini_mcts_15_29_20260317_203957",
])
print(f"MCTS 4.1-mini   L1: {len(mcts_41mini_l1)} | L4: {len(mcts_41mini_l4)} | L9: {len(mcts_41mini_l9)}")

# MCTS — o4-mini
mcts_o4mini_l1 = load_mcts([
    "mp_l1_o4mini_mcts_0_49_20260318_033536",
    "mp_l1_o4mini_mcts_50_99_20260318_033536",
    "mp_l1_o4mini_mcts_89_99_20260318_124004",
])
mcts_o4mini_l4 = load_mcts([])   # not started yet
mcts_o4mini_l9 = load_mcts([
    "mp_l9_o4mini_mcts_0_14_20260317_210557",
    "mp_l9_o4mini_mcts_15_29_20260317_210557",
])
print(f"MCTS o4-mini    L1: {len(mcts_o4mini_l1)} | L4: {len(mcts_o4mini_l4)} | L9: {len(mcts_o4mini_l9)}")


# ── Experiment registry ────────────────────────────────────────────────────────
# Format: "Name": (model, method, {len: df})

experiments = {
    "SSCoT (4.1-mini)": (
        "gpt-4.1-mini", "Pl CoT+Critique",
        {1: sscot_41mini_l1, 4: sscot_41mini_l4, 9: sscot_41mini_l9},
    ),
    "SSCoT (o4-mini)": (
        "o4-mini", "Pl CoT+Critique",
        {1: sscot_o4mini_l1, 4: sscot_o4mini_l4, 9: sscot_o4mini_l9},
    ),
    "AF Operator (4.1-mini)": (
        "gpt-4.1-mini", "Op Iterative",
        {1: af_op_41mini_l1, 4: af_op_41mini_l4, 9: af_op_41mini_l9},
    ),
    "AF Operator (o4-mini)": (
        "o4-mini", "Op Iterative",
        {1: af_op_o4mini_l1, 4: af_op_o4mini_l4, 9: af_op_o4mini_l9},
    ),
    "AF Pipeline (4.1-mini)": (
        "gpt-4.1-mini", "Pl Iterative",
        {1: af_pl_41mini_l1, 4: af_pl_41mini_l4, 9: af_pl_41mini_l9},
    ),
    "AF Pipeline (o4-mini)": (
        "o4-mini", "Pl Iterative",
        {1: af_pl_o4mini_l1, 4: af_pl_o4mini_l4, 9: af_pl_o4mini_l9},
    ),
    "MCTS (4.1-mini)": (
        "gpt-4.1-mini", "Op MCTS",
        {1: mcts_41mini_l1, 4: mcts_41mini_l4, 9: mcts_41mini_l9},
    ),
    "MCTS (o4-mini)": (
        "o4-mini", "Op MCTS",
        {1: mcts_o4mini_l1, 4: mcts_o4mini_l4, 9: mcts_o4mini_l9},
    ),
}


# ── Overall Sheet ─────────────────────────────────────────────────────────────

def overall_stats(df):
    if df is None or df.empty:
        return None, None, None, None
    n       = len(df)
    correct = int(df["is_correct"].sum())
    cost    = df["cost"].mean()            if n else None
    latency = df["latency_seconds"].mean() if n else None
    return correct, n, cost, latency


rows_overall = []
for exp_name, (model, method, len_dfs) in experiments.items():
    for length, df in sorted(len_dfs.items()):
        correct, n, cost, lat = overall_stats(df)
        acc = round(correct / n, 4) if n else "N/A"
        rows_overall.append({
            "Experiment":      exp_name,
            "Model":           model,
            "Method":          method,
            "Length":          f"L{length}",
            "Cases Evaluated": n if n is not None else 0,
            "Correct":         correct if correct is not None else 0,
            "Accuracy":        acc,
            "Avg Cost ($)":    round(cost, 6) if cost is not None else "N/A",
            "Avg Latency (s)": round(lat,  2) if lat  is not None else "N/A",
        })

df_overall = pd.DataFrame(rows_overall)


# ── Per-length sheets ─────────────────────────────────────────────────────────

def build_length_sheet(target_len):
    all_case_ids = set()
    exp_data = {}

    for exp_name, (model, method, len_dfs) in experiments.items():
        df = len_dfs.get(target_len)
        if df is not None and not df.empty:
            subset = df[df["len"] == target_len].copy()
            exp_data[exp_name] = subset.set_index("case_id")["is_correct"].to_dict()
            all_case_ids |= set(subset["case_id"])

    if not all_case_ids:
        return pd.DataFrame()

    def sort_key(cid):
        parts = str(cid).split("_")
        return (int(parts[0]), int(parts[1])) if len(parts) == 2 else (0, 0)

    rows = []
    for cid in sorted(all_case_ids, key=sort_key):
        row = {"Case ID": cid}
        for col, mapping in exp_data.items():
            row[col] = int(mapping.get(cid, "N/A")) if mapping.get(cid, "N/A") != "N/A" else "N/A"
        rows.append(row)

    return pd.DataFrame(rows)


df_l1 = build_length_sheet(1)
df_l4 = build_length_sheet(4)
df_l9 = build_length_sheet(9)


# ── Remaining Sheet ───────────────────────────────────────────────────────────

rows_remaining = []
for exp_name, (model, method, len_dfs) in experiments.items():
    for length, expected_ids in EXPECTED.items():
        df = len_dfs.get(length)
        if df is not None and not df.empty:
            done_ids = set(df["case_id"].apply(lambda x: int(str(x).split("_")[1])))
            missing  = sorted(expected_ids - done_ids)
        else:
            missing  = sorted(expected_ids)
        rows_remaining.append({
            "Experiment": exp_name,
            "Model":      model,
            "Method":     method,
            "Length":     f"L{length}",
            "Expected":   len(expected_ids),
            "Completed":  len(expected_ids) - len(missing),
            "Remaining":  len(missing),
            "Status":     "✓ Done" if not missing else ("⚠ Partial" if len(missing) < len(expected_ids) else "✗ Not started"),
            "Missing Cases": str(missing) if missing else "",
        })

df_remaining = pd.DataFrame(rows_remaining)


# ── Write Excel ───────────────────────────────────────────────────────────────

with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
    df_overall.to_excel(writer,   sheet_name="Overall",   index=False)
    df_l1.to_excel(writer,        sheet_name="L1",        index=False)
    df_l4.to_excel(writer,        sheet_name="L4",        index=False)
    df_l9.to_excel(writer,        sheet_name="L9",        index=False)
    df_remaining.to_excel(writer, sheet_name="Remaining", index=False)

    from openpyxl.utils import get_column_letter
    for sheet in writer.sheets.values():
        for col_cells in sheet.columns:
            max_len = max((len(str(c.value)) for c in col_cells if c.value), default=10)
            sheet.column_dimensions[get_column_letter(col_cells[0].column)].width = min(max_len + 4, 60)

print(f"\nDone! Saved to: {OUT}")
print(f"\nOverall summary:")
print(df_overall.to_string(index=False))
