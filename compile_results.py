"""
compile_results.py — Experiment result compiler
Sources: run_l9.sh, run_l4.sh, run_sscot.sh

Outputs: results_analysis.xlsx with sheets:
  1. Overall        — avg accuracy, avg cost, avg latency per experiment
  2. L1             — per-case is_correct for each experiment
  3. L4             — per-case is_correct for each experiment
  4. L9             — per-case is_correct for each experiment
  5. Sources        — result CSV paths used

Run from: ~/transchema/
  python3 compile_results.py
"""

import os
import pandas as pd
from pathlib import Path

ROOT    = Path("/home/local/ASUAD/jrtandel/transchema")
AF_DIRS = ROOT / "AgentFlow" / "results"
MS_BASE = ROOT / "logs-auto-suggest-llm-21-04"
MCTS_DIRS = ROOT / "Langraph" / "results_langraph"
OUT     = ROOT / "results_analysis.xlsx"


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
    """Load AgentFlow results_summary.csv files."""
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
    """Load MCTS results_summary.csv files."""
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


def load_from_v5(sheet, col, target_len, avg_cost, avg_latency):
    """Load per-case results from results_analysis_v5.xlsx.
    Uses per-case is_correct from `col`, and fills avg cost/latency from Overall sheet.
    """
    v5_path = ROOT / "results_analysis_v5.xlsx"
    if not v5_path.exists():
        print(f"  WARNING: {v5_path} not found")
        return pd.DataFrame()
    df = pd.read_excel(v5_path, sheet_name=sheet)
    df = df[["Case ID", col]].rename(columns={"Case ID": "case_id", col: "is_correct"})
    df = df.dropna(subset=["is_correct"])
    df["case_id"]         = df["case_id"].astype(str)
    df["is_correct"]      = df["is_correct"].map(lambda v: bool(int(v)) if str(v) not in ("nan","") else False)
    df["cost"]            = avg_cost
    df["latency_seconds"] = avg_latency
    df["len"]             = target_len
    return df[["case_id", "len", "is_correct", "cost", "latency_seconds"]]


def load_ms_only(exp_dirs):
    """Load only multi_step.csv (CoT only, no critique)."""
    ms_paths = [MS_BASE / d / "results" / "multi_step.csv" for d in exp_dirs]
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
    ms_df["is_correct"]      = ms_df["ms_correct"].map(
        lambda v: True if str(v).strip().lower() in ("true", "1") else False
    )
    ms_df["cost"]            = pd.to_numeric(ms_df["cost"],            errors="coerce").fillna(0)
    ms_df["latency_seconds"] = pd.to_numeric(ms_df["latency_seconds"], errors="coerce").fillna(0)
    ms_df["len"]             = ms_df["case_id"].apply(extract_len)
    return ms_df[["case_id", "len", "is_correct", "cost", "latency_seconds"]]


def load_ms_critique(exp_dirs):
    """Load multistep + critique CSVs (multi_step.csv + critique.csv).
    Column mapping: Soft Match = dollar cost, Soft Acc = latency seconds.
    """
    ms_paths   = [MS_BASE / d / "results" / "multi_step.csv" for d in exp_dirs]
    crit_paths = [MS_BASE / d / "results" / "critique.csv"   for d in exp_dirs]

    ms_df   = concat_csvs(ms_paths)
    crit_df = concat_csvs(crit_paths)

    if ms_df.empty:
        return pd.DataFrame()

    ms_df = ms_df.rename(columns={
        "Length":     "case_id",
        "Hard Match": "ms_correct",
        "Soft Match": "cost",            # actual dollar cost
        "Soft Acc":   "latency_seconds", # actual elapsed seconds
    })
    ms_df["case_id"]         = ms_df["case_id"].astype(str)
    ms_df["ms_correct"]      = ms_df["ms_correct"].map(
        lambda v: True if str(v).strip().lower() in ("true", "1") else False
    )
    ms_df["cost"]            = pd.to_numeric(ms_df["cost"],            errors="coerce").fillna(0)
    ms_df["latency_seconds"] = pd.to_numeric(ms_df["latency_seconds"], errors="coerce").fillna(0)

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

_MS_L1_DIRS = ["len_1_rerun_without_materialization_0_100_20260305_013029"]
_MS_L4_DIRS = [
    "len_4_rerun_without_materialization_15_48_20260305_123232",
    "len_4_rerun_without_materialization_34_67_20260305_123137",
    "len_4_rerun_without_materialization_48_81_20260305_123238",
    "len_4_rerun_without_materialization_81_100_20260305_123252",
]
_MS_L9_DIRS = [
    "overnight_ms_l9_0_50_20260309_012433",
    "overnight_ms_l9_51_100_20260309_012433",
    "l9_run2_ms_74_100_20260309_184346",
]
_SSCOT_L1_DIRS = ["l1_run1_sscot_0_99_20260310_100327"]
_SSCOT_L4_DIRS = ["l4_run1_sscot_15_99_20260310_100327"]
_SSCOT_L9_DIRS = ["l9_run1_sscot_0_100_20260310_100327"]

# Operator-driven CoT (multistep only, no critique)
op_cot_l1 = load_ms_only(_MS_L1_DIRS)
op_cot_l4 = load_ms_only(_MS_L4_DIRS).drop_duplicates(subset="case_id", keep="last")
op_cot_l9 = load_ms_only(_MS_L9_DIRS).drop_duplicates(subset="case_id", keep="last")
print(f"Op CoT L1:             {len(op_cot_l1)} cases")
print(f"Op CoT L4:             {len(op_cot_l4)} cases")
print(f"Op CoT L9:             {len(op_cot_l9)} cases")

# Operator-driven Critique (multistep + critique)
op_crit_l1 = load_ms_critique(_MS_L1_DIRS)
op_crit_l4 = load_ms_critique(_MS_L4_DIRS).drop_duplicates(subset="case_id", keep="last")
op_crit_l9 = load_ms_critique(_MS_L9_DIRS).drop_duplicates(subset="case_id", keep="last")
print(f"Op Critique L1:        {len(op_crit_l1)} cases")
print(f"Op Critique L4:        {len(op_crit_l4)} cases")
print(f"Op Critique L9:        {len(op_crit_l9)} cases")

# Pipeline-driven CoT (SSCoT only, no critique)
pl_cot_l1 = load_ms_only(_SSCOT_L1_DIRS)
pl_cot_l4 = load_ms_only(_SSCOT_L4_DIRS)
pl_cot_l9 = load_ms_only(_SSCOT_L9_DIRS)
print(f"Pl CoT L1:             {len(pl_cot_l1)} cases")
print(f"Pl CoT L4:             {len(pl_cot_l4)} cases")
print(f"Pl CoT L9:             {len(pl_cot_l9)} cases")

# Pipeline-driven Critique (SSCoT + critique)
pl_crit_l1 = load_ms_critique(_SSCOT_L1_DIRS)
pl_crit_l4 = load_ms_critique(_SSCOT_L4_DIRS)
pl_crit_l9 = load_ms_critique(_SSCOT_L9_DIRS)
print(f"Pl Critique L1:        {len(pl_crit_l1)} cases")
print(f"Pl Critique L4:        {len(pl_crit_l4)} cases")
print(f"Pl Critique L9:        {len(pl_crit_l9)} cases")

# ── AgentFlow Operator (run_l4.sh + run_l9.sh) ────────────────────────────────
af_op_l1 = load_agentflow([
    "l1_run1_af_op_0_49_20260310_112706",
    "l1_run1_af_op_50_99_20260310_112706",
])
af_op_l4 = load_agentflow([
    "l4_run1_af_op_15_57_20260310_001841",
    "l4_run1_af_op_58_99_20260310_001840",
])
af_op_l9 = load_agentflow([
    "l9_run2_af_op_0_50_20260309_190123",
    "l9_run2_af_op_51_100_20260309_190123",
])
print(f"AF Operator L1:        {len(af_op_l1)} cases")
print(f"AF Operator L4:        {len(af_op_l4)} cases")
print(f"AF Operator L9:        {len(af_op_l9)} cases")

# ── AF Operator L1 top-up (cases 90-100, other server) ───────────────────────
af_op_l1_topup = load_agentflow(["agentflow_operator_l1_90_100_20260310_234024"])
if af_op_l1_topup.empty:
    # Fall back to per-case data from results_analysis_v5.xlsx
    af_op_l1_topup = load_from_v5("L1", "Operator-driven Operator(90-100)", 1, avg_cost=0.023535, avg_latency=70.09)
    print(f"AF Operator L1 top-up (from v5): {len(af_op_l1_topup)} cases")
else:
    print(f"AF Operator L1 top-up: {len(af_op_l1_topup)} cases")
af_op_l1 = pd.concat([af_op_l1, af_op_l1_topup], ignore_index=True).drop_duplicates(subset="case_id", keep="last")
print(f"AF Operator L1 merged: {len(af_op_l1)} cases")

# ── AgentFlow Pipeline (run_l4.sh + run_l9.sh + other server) ────────────────
af_pl_l1 = load_agentflow(["agentflow_pipeline_l1_20260310_234018"])
if af_pl_l1.empty:
    af_pl_l1 = load_from_v5("L1", "Pipeline-driven Pipeline", 1, avg_cost=0.028786, avg_latency=95.13)
    print(f"AF Pipeline L1 (from v5): {len(af_pl_l1)} cases")
af_pl_l4 = load_agentflow([
    "l4_run1_af_pl_15_57_20260310_034423",
    "l4_run1_af_pl_58_99_20260310_034423",
])
af_pl_l9 = load_agentflow([
    "l9_run2_af_pl_0_50_20260310_000446",
    "l9_run2_af_pl_51_100_20260310_000446",
])
print(f"AF Pipeline L1:        {len(af_pl_l1)} cases")
print(f"AF Pipeline L4:        {len(af_pl_l4)} cases")
print(f"AF Pipeline L9:        {len(af_pl_l9)} cases")

# ── MCTS (run_l4.sh + run_l9.sh + other server) ───────────────────────────────
mcts_l1 = load_mcts([d.name for d in MCTS_DIRS.glob("mcts_length1_batch_*")])
if mcts_l1.empty:
    mcts_l1 = load_from_v5("L1", "Operator-driven MCTS", 1, avg_cost=0.016261, avg_latency=127.40)
    print(f"MCTS L1 (from v5): {len(mcts_l1)} cases")
mcts_l4 = load_mcts([
    "l4_run1_mcts_15_57_20260310_062719",
    "l4_run1_mcts_58_99_20260310_062719",
])
# L9 MCTS: local runs (cases 0-69) + other-server remaining (cases 70-100)
mcts_l9_local = load_mcts([
    "l9_run2_mcts_0_50_20260310_081151",
    "l9_run2_mcts_51_100_20260310_081151",
])
mcts_l9_remote = load_mcts([d.name for d in MCTS_DIRS.glob("mcts_length9_batch_*")])
if mcts_l9_remote.empty:
    mcts_l9_remote = load_from_v5("L9", "Operator-driven MCTS", 9, avg_cost=0.034417, avg_latency=111.92)
    print(f"MCTS L9 remote (from v5): {len(mcts_l9_remote)} cases")
mcts_l9 = pd.concat([mcts_l9_local, mcts_l9_remote], ignore_index=True).drop_duplicates(subset="case_id", keep="last")
print(f"MCTS L1:               {len(mcts_l1)} cases")
print(f"MCTS L4:               {len(mcts_l4)} cases")
print(f"MCTS L9:               {len(mcts_l9)} cases")


# ── Experiment registry ───────────────────────────────────────────────────────
# Format: "Name": (granularity, {len: df}, {len: [source paths]})

# ── Experiment registry (matches Table 6 nomenclature) ────────────────────────
# Format: "Name": (Decision, Planning, {len: df}, {len: [source paths]})
experiments = {
    # ── Operator-driven ───────────────────────────────────────────────────────
    "Op CoT": (
        "Operator-driven", "CoT",
        {1: op_cot_l1, 4: op_cot_l4, 9: op_cot_l9},
        {1: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _MS_L1_DIRS],
         4: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _MS_L4_DIRS],
         9: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _MS_L9_DIRS]},
    ),
    "Op Critique": (
        "Operator-driven", "Critique",
        {1: op_crit_l1, 4: op_crit_l4, 9: op_crit_l9},
        {1: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _MS_L1_DIRS],
         4: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _MS_L4_DIRS],
         9: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _MS_L9_DIRS]},
    ),
    "Op Iterative": (
        "Operator-driven", "Iterative",
        {1: af_op_l1, 4: af_op_l4, 9: af_op_l9},
        {1: [str(AF_DIRS / "l1_run1_af_op_0_49_20260310_112706"  / "results_summary.csv"),
             str(AF_DIRS / "l1_run1_af_op_50_99_20260310_112706" / "results_summary.csv"),
             str(AF_DIRS / "agentflow_operator_l1_90_100_20260310_234024" / "results_summary.csv")],
         4: [str(AF_DIRS / "l4_run1_af_op_15_57_20260310_001841" / "results_summary.csv"),
             str(AF_DIRS / "l4_run1_af_op_58_99_20260310_001840" / "results_summary.csv")],
         9: [str(AF_DIRS / "l9_run2_af_op_0_50_20260309_190123"  / "results_summary.csv"),
             str(AF_DIRS / "l9_run2_af_op_51_100_20260309_190123"/ "results_summary.csv")]},
    ),
    "Op MCTS": (
        "Operator-driven", "MCTS",
        {1: mcts_l1, 4: mcts_l4, 9: mcts_l9},
        {1: [str(p / "results_summary.csv") for p in MCTS_DIRS.glob("mcts_length1_batch_*")],
         4: [str(MCTS_DIRS / "l4_run1_mcts_15_57_20260310_062719" / "results_summary.csv"),
             str(MCTS_DIRS / "l4_run1_mcts_58_99_20260310_062719" / "results_summary.csv")],
         9: [str(MCTS_DIRS / "l9_run2_mcts_0_50_20260310_081151"  / "results_summary.csv"),
             str(MCTS_DIRS / "l9_run2_mcts_51_100_20260310_081151"/ "results_summary.csv")]},
    ),
    # ── Pipeline-driven ───────────────────────────────────────────────────────
    "Pl CoT": (
        "Pipeline-driven", "CoT",
        {1: pl_cot_l1, 4: pl_cot_l4, 9: pl_cot_l9},
        {1: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _SSCOT_L1_DIRS],
         4: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _SSCOT_L4_DIRS],
         9: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _SSCOT_L9_DIRS]},
    ),
    "Pl Critique": (
        "Pipeline-driven", "Critique",
        {1: pl_crit_l1, 4: pl_crit_l4, 9: pl_crit_l9},
        {1: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _SSCOT_L1_DIRS],
         4: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _SSCOT_L4_DIRS],
         9: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _SSCOT_L9_DIRS]},
    ),
    "Pl Iterative": (
        "Pipeline-driven", "Iterative",
        {1: af_pl_l1, 4: af_pl_l4, 9: af_pl_l9},
        {1: [str(AF_DIRS / "agentflow_pipeline_l1_20260310_234018" / "results_summary.csv")],
         4: [str(AF_DIRS / "l4_run1_af_pl_15_57_20260310_034423" / "results_summary.csv"),
             str(AF_DIRS / "l4_run1_af_pl_58_99_20260310_034423" / "results_summary.csv")],
         9: [str(AF_DIRS / "l9_run2_af_pl_0_50_20260310_000446"  / "results_summary.csv"),
             str(AF_DIRS / "l9_run2_af_pl_51_100_20260310_000446"/ "results_summary.csv")]},
    ),
}


# ── Overall Sheet ─────────────────────────────────────────────────────────────

def overall_stats(df):
    if df is None or df.empty:
        return None, None, None, None
    n = len(df)
    correct = int(df["is_correct"].sum())
    cost    = df["cost"].mean()            if n else None
    latency = df["latency_seconds"].mean() if n else None
    return correct, n, cost, latency

rows_overall = []
rows_sources = []
for exp_name, (decision, planning, len_dfs, len_sources) in experiments.items():
    for length, df in sorted(len_dfs.items()):
        correct, n, cost, lat = overall_stats(df)
        rows_overall.append({
            "Decision":        decision,
            "Planning":        planning,
            "Length":          f"L{length}",
            "Cases Evaluated": n if n is not None else 0,
            "Correct":         correct if correct is not None else "N/A",
            "Avg Cost ($)":    round(cost, 6) if cost is not None else "N/A",
            "Avg Latency (s)": round(lat,  2) if lat  is not None else "N/A",
        })
        for src in len_sources.get(length, []):
            rows_sources.append({
                "Decision":   decision,
                "Planning":   planning,
                "Length":     f"L{length}",
                "Source CSV": src,
                "Exists":     os.path.exists(src),
            })

df_overall = pd.DataFrame(rows_overall)


# ── Per-length sheets ─────────────────────────────────────────────────────────

def build_length_sheet(target_len):
    all_case_ids = set()
    exp_data = {}

    for exp_name, (decision, planning, len_dfs, _) in experiments.items():
        df = len_dfs.get(target_len)
        col_label = f"{decision}\n{planning}"
        if df is not None and not df.empty:
            subset = df[df["len"] == target_len].copy()
            exp_data[col_label] = subset.set_index("case_id")["is_correct"].to_dict()
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
            row[col] = mapping.get(cid, "N/A")
        rows.append(row)

    return pd.DataFrame(rows)

df_l1 = build_length_sheet(1)
df_l4 = build_length_sheet(4)
df_l9 = build_length_sheet(9)


# ── Remaining Sheet ───────────────────────────────────────────────────────────
# Expected case ranges per length
EXPECTED = {1: set(range(0, 100)), 4: set(range(15, 100)), 9: set(range(0, 101))}

rows_remaining = []
for exp_name, (decision, planning, len_dfs, _) in experiments.items():
    for length, expected_ids in EXPECTED.items():
        df = len_dfs.get(length)
        if df is not None and not df.empty:
            done_ids = set(df["case_id"].apply(lambda x: int(str(x).split("_")[1])))
            missing = sorted(expected_ids - done_ids)
        else:
            missing = sorted(expected_ids)
        rows_remaining.append({
            "Decision":      decision,
            "Planning":      planning,
            "Length":        f"L{length}",
            "Expected":      len(expected_ids),
            "Completed":     len(expected_ids) - len(missing),
            "Remaining":     len(missing),
            "Status":        "✓ Done" if not missing else ("⚠ Partial" if len(missing) < len(expected_ids) else "✗ Not started"),
            "Missing Cases": str(missing) if missing else "",
        })

df_remaining = pd.DataFrame(rows_remaining)

# ── Write Excel ───────────────────────────────────────────────────────────────

df_sources = pd.DataFrame(rows_sources)

with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
    df_overall.to_excel(writer, sheet_name="Overall", index=False)
    df_l1.to_excel(writer, sheet_name="L1", index=False)
    df_l4.to_excel(writer, sheet_name="L4", index=False)
    df_l9.to_excel(writer, sheet_name="L9", index=False)
    df_remaining.to_excel(writer, sheet_name="Remaining", index=False)
    df_sources.to_excel(writer, sheet_name="Sources", index=False)

    from openpyxl.utils import get_column_letter
    for sheet in writer.sheets.values():
        for col_cells in sheet.columns:
            max_len = max((len(str(c.value)) for c in col_cells if c.value), default=10)
            sheet.column_dimensions[get_column_letter(col_cells[0].column)].width = min(max_len + 4, 60)

print(f"\nDone! Saved to: {OUT}")
print(f"\nOverall summary:")
print(df_overall.to_string(index=False))
