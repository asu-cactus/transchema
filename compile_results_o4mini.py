"""
compile_results_o4mini.py — o4-mini experiment result compiler

Outputs: results_analysis_o4mini.xlsx with sheets:
  1. Overall    — avg accuracy, avg cost, avg latency per experiment
  2. L1         — per-case is_correct for each experiment
  3. L4         — per-case is_correct for each experiment
  4. L9         — per-case is_correct for each experiment
  5. Remaining  — cases not yet completed
  6. Sources    — result CSV paths used

Run from: ~/transchema/
  python3 compile_results_o4mini.py
"""

import os
import pandas as pd
from pathlib import Path

ROOT    = Path(__file__).resolve().parent
AF_DIRS = ROOT / "AgentFlow" / "results"
LG_DIRS = ROOT / "Langraph" / "results_langraph"
MS_BASE = ROOT / "logs-auto-suggest-llm-21-04"
OUT     = ROOT / "results_analysis_o4mini.xlsx"


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


def load_ms_only(exp_dirs):
    """Load multi_step.csv only (CoT, no critique)."""
    paths = [MS_BASE / d / "results" / "multi_step.csv" for d in exp_dirs]
    df = concat_csvs(paths)
    if df.empty:
        return pd.DataFrame()
    df = df.rename(columns={"Length": "case_id", "Hard Match": "ms_correct",
                             "Soft Match": "cost", "Soft Acc": "latency_seconds"})
    df["case_id"]         = df["case_id"].astype(str)
    df["is_correct"]      = df["ms_correct"].map(lambda v: True if str(v).strip().lower() in ("true","1") else False)
    df["cost"]            = pd.to_numeric(df["cost"],            errors="coerce").fillna(0)
    df["latency_seconds"] = pd.to_numeric(df["latency_seconds"], errors="coerce").fillna(0)
    df["len"]             = df["case_id"].apply(extract_len)
    return df[["case_id", "len", "is_correct", "cost", "latency_seconds"]]


def load_ms_critique(exp_dirs):
    """Load multi_step.csv + critique.csv (correct if either passes)."""
    ms_df   = concat_csvs([MS_BASE / d / "results" / "multi_step.csv" for d in exp_dirs])
    crit_df = concat_csvs([MS_BASE / d / "results" / "critique.csv"   for d in exp_dirs])
    if ms_df.empty:
        return pd.DataFrame()
    ms_df = ms_df.rename(columns={"Length": "case_id", "Hard Match": "ms_correct",
                                   "Soft Match": "cost", "Soft Acc": "latency_seconds"})
    ms_df["case_id"]         = ms_df["case_id"].astype(str)
    ms_df["ms_correct"]      = ms_df["ms_correct"].map(lambda v: True if str(v).strip().lower() in ("true","1") else False)
    ms_df["cost"]            = pd.to_numeric(ms_df["cost"],            errors="coerce").fillna(0)
    ms_df["latency_seconds"] = pd.to_numeric(ms_df["latency_seconds"], errors="coerce").fillna(0)
    if not crit_df.empty:
        crit_df = crit_df.rename(columns={"Length": "case_id", "Hard Match": "crit_correct",
                                           "Soft Match": "crit_cost", "Soft Acc": "crit_latency"})
        crit_df["case_id"]      = crit_df["case_id"].astype(str)
        crit_df["crit_correct"] = crit_df["crit_correct"].map(lambda v: True if str(v).strip().lower() in ("true","1") else False)
        crit_df["crit_cost"]    = pd.to_numeric(crit_df.get("crit_cost"),    errors="coerce").fillna(0)
        crit_df["crit_latency"] = pd.to_numeric(crit_df.get("crit_latency"), errors="coerce").fillna(0)
        crit_best = crit_df.groupby("case_id").agg(
            crit_correct=("crit_correct", "any"),
            crit_cost=("crit_cost", "sum"),
            crit_latency=("crit_latency", "sum")).reset_index()
        ms_df = ms_df.merge(crit_best, on="case_id", how="left")
        ms_df["crit_correct"] = ms_df["crit_correct"].fillna(False)
        ms_df["crit_cost"]    = ms_df["crit_cost"].fillna(0)
        ms_df["crit_latency"] = ms_df["crit_latency"].fillna(0)
    else:
        ms_df["crit_correct"] = False; ms_df["crit_cost"] = 0; ms_df["crit_latency"] = 0
    ms_df["is_correct"]      = ms_df["ms_correct"] | ms_df["crit_correct"]
    ms_df["cost"]            += ms_df["crit_cost"]
    ms_df["latency_seconds"] += ms_df["crit_latency"]
    ms_df["len"]              = ms_df["case_id"].apply(extract_len)
    return ms_df[["case_id", "len", "is_correct", "cost", "latency_seconds"]]


def load_langraph(exp_dirs):
    """Load Langraph/MCTS results_summary.csv files."""
    paths = [LG_DIRS / d / "results_summary.csv" for d in exp_dirs]
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


# ── Load all o4-mini experiments ──────────────────────────────────────────────

# L1 Operator  (223258 is the run with data; 223024 has 0 rows)
af_op_l1 = load_agentflow([
    "l1_o4mini_af_op_0_49_20260311_223258",
    "l1_o4mini_af_op_50_99_20260311_223258",
])
af_op_l1 = af_op_l1.drop_duplicates(subset="case_id", keep="last")

# L4 Operator  (222043=41 rows, 223442=43 rows — concat and keep latest per case_id)
af_op_l4 = load_agentflow([
    "l4_o4mini_af_op_15_57_20260311_222043",
    "l4_o4mini_af_op_15_57_20260311_223442",
    "l4_o4mini_af_op_58_99_20260311_223442",
])
af_op_l4 = af_op_l4.drop_duplicates(subset="case_id", keep="last")

# L9 Operator
af_op_l9 = load_agentflow([
    "l9_o4mini_af_op_0_50_20260311_223533",
    "l9_o4mini_af_op_51_100_20260311_223533",
])
af_op_l9 = af_op_l9.drop_duplicates(subset="case_id", keep="last")

# L1 Pipeline (rerun with fix)
af_pl_l1 = load_agentflow([
    "l1_o4mini_af_pl_0_33_20260312_110100",
    "l1_o4mini_af_pl_34_66_20260312_110100",
    "l1_o4mini_af_pl_67_99_20260312_110100",
])
af_pl_l1 = af_pl_l1.drop_duplicates(subset="case_id", keep="last")

# L4 Pipeline (rerun with fix — partial, will update when complete)
af_pl_l4 = load_agentflow([
    "l4_o4mini_af_pl_15_43_20260312_110107",
    "l4_o4mini_af_pl_44_71_20260312_110108",
    "l4_o4mini_af_pl_72_99_20260312_110108",
])
af_pl_l4 = af_pl_l4.drop_duplicates(subset="case_id", keep="last")

# L9 Pipeline (rerun with fix — partial, will update when complete)
af_pl_l9 = load_agentflow([
    "l9_o4mini_af_pl_0_33_20260312_110116",
    "l9_o4mini_af_pl_34_67_20260312_110116",
    "l9_o4mini_af_pl_68_100_20260312_110116",
])
af_pl_l9 = af_pl_l9.drop_duplicates(subset="case_id", keep="last")

# ── Multistep (o4-mini) — critique_data.py ────────────────────────────────────
_MS_O4_L1  = ["l1_o4mini_ms_0_100_20260316_173713"]
_MS_O4_L4  = [
    "l4_o4mini_ms_15_99_20260316_173713",    # only 4_15 completed (OOM on 4_16)
    "l4_o4mini_ms_18_44_20260317_123553",    # cases 18–44
    "l4_o4mini_ms_45_71_20260317_123643",    # cases 45–71
    "l4_o4mini_ms_72_99_20260317_123622",    # cases 72–99
]
_MS_O4_L9  = ["l9_o4mini_ms_0_50_20260316_173713", "l9_o4mini_ms_51_100_20260316_173713"]

ms_cot_l1 = load_ms_only(_MS_O4_L1)
ms_cot_l4 = load_ms_only(_MS_O4_L4).drop_duplicates(subset="case_id", keep="last")
ms_cot_l9 = load_ms_only(_MS_O4_L9).drop_duplicates(subset="case_id", keep="last")

ms_crit_l1 = load_ms_critique(_MS_O4_L1)
ms_crit_l4 = load_ms_critique(_MS_O4_L4).drop_duplicates(subset="case_id", keep="last")
ms_crit_l9 = load_ms_critique(_MS_O4_L9).drop_duplicates(subset="case_id", keep="last")

print(f"MS CoT     L1: {len(ms_cot_l1)} cases")
print(f"MS CoT     L4: {len(ms_cot_l4)} cases")
print(f"MS CoT     L9: {len(ms_cot_l9)} cases")
print(f"MS Critique L1: {len(ms_crit_l1)} cases")
print(f"MS Critique L4: {len(ms_crit_l4)} cases")
print(f"MS Critique L9: {len(ms_crit_l9)} cases")

# ── SSCoT (o4-mini) — critique_data.py ────────────────────────────────────────
_SSCOT_O4_L1 = ["l1_o4mini_sscot_0_100_20260316_191442"]
_SSCOT_O4_L4 = ["l4_o4mini_sscot_15_99_20260316_174514"]
_SSCOT_O4_L9 = ["l9_o4mini_sscot_0_100_20260316_195251"]

sscot_cot_l1 = load_ms_only(_SSCOT_O4_L1)
sscot_cot_l4 = load_ms_only(_SSCOT_O4_L4).drop_duplicates(subset="case_id", keep="last")
sscot_cot_l9 = load_ms_only(_SSCOT_O4_L9).drop_duplicates(subset="case_id", keep="last")

sscot_crit_l1 = load_ms_critique(_SSCOT_O4_L1)
sscot_crit_l4 = load_ms_critique(_SSCOT_O4_L4).drop_duplicates(subset="case_id", keep="last")
sscot_crit_l9 = load_ms_critique(_SSCOT_O4_L9).drop_duplicates(subset="case_id", keep="last")

print(f"SSCoT CoT     L1: {len(sscot_cot_l1)} cases")
print(f"SSCoT CoT     L4: {len(sscot_cot_l4)} cases")
print(f"SSCoT CoT     L9: {len(sscot_cot_l9)} cases")
print(f"SSCoT Critique L1: {len(sscot_crit_l1)} cases")
print(f"SSCoT Critique L4: {len(sscot_crit_l4)} cases")
print(f"SSCoT Critique L9: {len(sscot_crit_l9)} cases")

# ── Materialization (o4-mini) — critique_data.py ─────────────────────────────
_MAT_O4_L1 = [
    "l1_o4mini_ms_mat_0_49_20260318_172807",
    "l1_o4mini_ms_mat_50_99_20260318_172808",
]
_MAT_O4_L4 = [
    "l4_o4mini_ms_mat_15_56_20260318_183306",
    "l4_o4mini_ms_mat_57_99_20260318_183306",
]
_MAT_O4_L9 = [
    "l9_o4mini_ms_mat_0_50_20260318_215540",
    "l9_o4mini_ms_mat_51_100_20260318_215540",
]

mat_cot_l1 = load_ms_only(_MAT_O4_L1).drop_duplicates(subset="case_id", keep="last")
mat_cot_l4 = load_ms_only(_MAT_O4_L4).drop_duplicates(subset="case_id", keep="last")
mat_cot_l9 = load_ms_only(_MAT_O4_L9).drop_duplicates(subset="case_id", keep="last")

mat_crit_l1 = load_ms_critique(_MAT_O4_L1).drop_duplicates(subset="case_id", keep="last")
mat_crit_l4 = load_ms_critique(_MAT_O4_L4).drop_duplicates(subset="case_id", keep="last")
mat_crit_l9 = load_ms_critique(_MAT_O4_L9).drop_duplicates(subset="case_id", keep="last")

print(f"Mat CoT     L1: {len(mat_cot_l1)} cases")
print(f"Mat CoT     L4: {len(mat_cot_l4)} cases")
print(f"Mat CoT     L9: {len(mat_cot_l9)} cases")
print(f"Mat Critique L1: {len(mat_crit_l1)} cases")
print(f"Mat Critique L4: {len(mat_crit_l4)} cases")
print(f"Mat Critique L9: {len(mat_crit_l9)} cases")

# MCTS (o4-mini) — Langraph
mcts_l1 = load_langraph([
    "l1_o4mini_mcts_0_49_20260315_192556",
    "l1_o4mini_mcts_50_99_20260315_192556",
])
mcts_l1 = mcts_l1.drop_duplicates(subset="case_id", keep="last")

mcts_l4 = load_langraph([
    "l4_o4mini_mcts_15_57_20260315_192626",   # only 4_15 completed before OOM
    "l4_o4mini_mcts_18_30_20260316_103725",
    "l4_o4mini_mcts_31_43_20260316_103732",
    "l4_o4mini_mcts_44_57_20260316_103739",
    "l4_o4mini_mcts_58_99_20260315_192626",
])
mcts_l4 = mcts_l4.drop_duplicates(subset="case_id", keep="last")

mcts_l9 = load_langraph([
    "l9_o4mini_mcts_0_50_20260315_192652",
    "l9_o4mini_mcts_51_100_20260315_192652",
])
mcts_l9 = mcts_l9.drop_duplicates(subset="case_id", keep="last")

print(f"AF Op  L1: {len(af_op_l1)} cases")
print(f"AF Op  L4: {len(af_op_l4)} cases")
print(f"AF Op  L9: {len(af_op_l9)} cases")
print(f"AF Pl  L1: {len(af_pl_l1)} cases")
print(f"AF Pl  L4: {len(af_pl_l4)} cases")
print(f"AF Pl  L9: {len(af_pl_l9)} cases")
print(f"MCTS   L1: {len(mcts_l1)} cases")
print(f"MCTS   L4: {len(mcts_l4)} cases")
print(f"MCTS   L9: {len(mcts_l9)} cases")


# ── Experiment registry ───────────────────────────────────────────────────────
# Format: "Name": (Decision, Planning, {len: df}, {len: [source paths]})

experiments = {
    "Op CoT (o4-mini)": (
        "Operator-driven", "CoT (o4-mini)",
        {1: ms_cot_l1, 4: ms_cot_l4, 9: ms_cot_l9},
        {1: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _MS_O4_L1],
         4: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _MS_O4_L4],
         9: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _MS_O4_L9]},
    ),
    "Op Critique (o4-mini)": (
        "Operator-driven", "Critique (o4-mini)",
        {1: ms_crit_l1, 4: ms_crit_l4, 9: ms_crit_l9},
        {1: [str(MS_BASE / d / "results" / "critique.csv") for d in _MS_O4_L1],
         4: [str(MS_BASE / d / "results" / "critique.csv") for d in _MS_O4_L4],
         9: [str(MS_BASE / d / "results" / "critique.csv") for d in _MS_O4_L9]},
    ),
    "Pl CoT (o4-mini)": (
        "Pipeline-driven", "CoT (o4-mini)",
        {1: sscot_cot_l1, 4: sscot_cot_l4, 9: sscot_cot_l9},
        {1: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _SSCOT_O4_L1],
         4: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _SSCOT_O4_L4],
         9: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _SSCOT_O4_L9]},
    ),
    "Pl Critique (o4-mini)": (
        "Pipeline-driven", "Critique (o4-mini)",
        {1: sscot_crit_l1, 4: sscot_crit_l4, 9: sscot_crit_l9},
        {1: [str(MS_BASE / d / "results" / "critique.csv") for d in _SSCOT_O4_L1],
         4: [str(MS_BASE / d / "results" / "critique.csv") for d in _SSCOT_O4_L4],
         9: [str(MS_BASE / d / "results" / "critique.csv") for d in _SSCOT_O4_L9]},
    ),
    "Op CoT+Mat (o4-mini)": (
        "Operator-driven", "CoT+Materialization (o4-mini)",
        {1: mat_cot_l1, 4: mat_cot_l4, 9: mat_cot_l9},
        {1: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _MAT_O4_L1],
         4: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _MAT_O4_L4],
         9: [str(MS_BASE / d / "results" / "multi_step.csv") for d in _MAT_O4_L9]},
    ),
    "Op Critique+Mat (o4-mini)": (
        "Operator-driven", "Critique+Materialization (o4-mini)",
        {1: mat_crit_l1, 4: mat_crit_l4, 9: mat_crit_l9},
        {1: [str(MS_BASE / d / "results" / "critique.csv") for d in _MAT_O4_L1],
         4: [str(MS_BASE / d / "results" / "critique.csv") for d in _MAT_O4_L4],
         9: [str(MS_BASE / d / "results" / "critique.csv") for d in _MAT_O4_L9]},
    ),
    "Op Iterative (o4-mini)": (
        "Operator-driven", "Iterative (o4-mini)",
        {1: af_op_l1, 4: af_op_l4, 9: af_op_l9},
        {1: [str(AF_DIRS / "l1_o4mini_af_op_0_49_20260311_223258"  / "results_summary.csv"),
             str(AF_DIRS / "l1_o4mini_af_op_50_99_20260311_223258" / "results_summary.csv")],
         4: [str(AF_DIRS / "l4_o4mini_af_op_15_57_20260311_222043" / "results_summary.csv"),
             str(AF_DIRS / "l4_o4mini_af_op_15_57_20260311_223442" / "results_summary.csv"),
             str(AF_DIRS / "l4_o4mini_af_op_58_99_20260311_223442" / "results_summary.csv")],
         9: [str(AF_DIRS / "l9_o4mini_af_op_0_50_20260311_223533"  / "results_summary.csv"),
             str(AF_DIRS / "l9_o4mini_af_op_51_100_20260311_223533"/ "results_summary.csv")]},
    ),
    "Pl Iterative (o4-mini)": (
        "Pipeline-driven", "Iterative (o4-mini)",
        {1: af_pl_l1, 4: af_pl_l4, 9: af_pl_l9},
        {1: [str(AF_DIRS / "l1_o4mini_af_pl_0_33_20260312_110100"  / "results_summary.csv"),
             str(AF_DIRS / "l1_o4mini_af_pl_34_66_20260312_110100" / "results_summary.csv"),
             str(AF_DIRS / "l1_o4mini_af_pl_67_99_20260312_110100" / "results_summary.csv")],
         4: [str(AF_DIRS / "l4_o4mini_af_pl_15_43_20260312_110107" / "results_summary.csv"),
             str(AF_DIRS / "l4_o4mini_af_pl_44_71_20260312_110108" / "results_summary.csv"),
             str(AF_DIRS / "l4_o4mini_af_pl_72_99_20260312_110108" / "results_summary.csv")],
         9: [str(AF_DIRS / "l9_o4mini_af_pl_0_33_20260312_110116"  / "results_summary.csv"),
             str(AF_DIRS / "l9_o4mini_af_pl_34_67_20260312_110116" / "results_summary.csv"),
             str(AF_DIRS / "l9_o4mini_af_pl_68_100_20260312_110116"/ "results_summary.csv")]},
    ),
    "MCTS (o4-mini)": (
        "Operator-driven", "MCTS (o4-mini)",
        {1: mcts_l1, 4: mcts_l4, 9: mcts_l9},
        {1: [str(LG_DIRS / "l1_o4mini_mcts_0_49_20260315_192556"  / "results_summary.csv"),
             str(LG_DIRS / "l1_o4mini_mcts_50_99_20260315_192556" / "results_summary.csv")],
         4: [str(LG_DIRS / "l4_o4mini_mcts_15_57_20260315_192626"  / "results_summary.csv"),
             str(LG_DIRS / "l4_o4mini_mcts_18_30_20260316_103725"  / "results_summary.csv"),
             str(LG_DIRS / "l4_o4mini_mcts_31_43_20260316_103732"  / "results_summary.csv"),
             str(LG_DIRS / "l4_o4mini_mcts_44_57_20260316_103739"  / "results_summary.csv"),
             str(LG_DIRS / "l4_o4mini_mcts_58_99_20260315_192626"  / "results_summary.csv")],
         9: [str(LG_DIRS / "l9_o4mini_mcts_0_50_20260315_192652"  / "results_summary.csv"),
             str(LG_DIRS / "l9_o4mini_mcts_51_100_20260315_192652"/ "results_summary.csv")]},
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
    df_overall.to_excel(writer,   sheet_name="Overall",   index=False)
    df_l1.to_excel(writer,        sheet_name="L1",        index=False)
    df_l4.to_excel(writer,        sheet_name="L4",        index=False)
    df_l9.to_excel(writer,        sheet_name="L9",        index=False)
    df_remaining.to_excel(writer, sheet_name="Remaining", index=False)
    df_sources.to_excel(writer,   sheet_name="Sources",   index=False)

    from openpyxl.utils import get_column_letter
    for sheet in writer.sheets.values():
        for col_cells in sheet.columns:
            max_len = max((len(str(c.value)) for c in col_cells if c.value), default=10)
            sheet.column_dimensions[get_column_letter(col_cells[0].column)].width = min(max_len + 4, 60)

print(f"\nDone! Saved to: {OUT}")
print(f"\nOverall summary:")
print(df_overall.to_string(index=False))
