"""
analyze_tool_invocations.py — Tool invocation counts per case for all AgentFlow experiments.

Reads *_full_output.json for each case and counts how many times each tool was called.
Also adds correctness columns from results_analysis_monteprep.xlsx and SSCoT CSVs.

Output: tool_invocations.xlsx with sheets:
  - Operator_41mini  — per-case tool counts + correctness, gpt-4.1-mini operator runs
  - Operator_o4mini  — per-case tool counts + correctness, o4-mini operator runs
  - Pipeline_41mini  — per-case tool counts + correctness, gpt-4.1-mini pipeline runs
  - Pipeline_o4mini  — per-case tool counts + correctness, o4-mini pipeline runs
  - Summary          — avg invocations per experiment x tool

Correctness columns added per sheet:
  - af_correct            — whether AF solved the case (from results_analysis_monteprep.xlsx)
  - sscot_pass1_correct   — whether SSCoT (same model) solved it on pass-1
  - sscot_critique_correct — whether SSCoT (same model) solved it after critique

Run from: ~/transchema/
  python3 analyze_tool_invocations.py
"""

import json
import os
from pathlib import Path
from collections import defaultdict

import pandas as pd

ROOT    = Path(__file__).resolve().parent
AF_DIRS = ROOT / "AgentFlow" / "results"
OUT     = ROOT / "tool_invocations.xlsx"
SSCOT_BASE = ROOT / "logs-auto-suggest-llm-21-04"
RESULTS_XL = ROOT / "results_analysis_monteprep.xlsx"

# ── Tool groupings ────────────────────────────────────────────────────────────

OPERATOR_TOOLS = [
    "Configure_Join_Operator_Tool",
    "Configure_Union_Operator_Tool",
    "Configure_GroupBy_Aggregate_Operator_Tool",
    "Add_Pivot_Tool",
    "Add_Unpivot_Tool",
    "Code_Gen_And_Score_Tool",
    "Critique_Pipeline_Tool",
    "Start_Again_Tool",
]

PIPELINE_TOOLS = [
    "Create_New_Pipeline",
    "Refine_Existing_Pipeline",
    "Code_Generator_Tool",
    "Finalize_Pipeline_Tool",
]

# ── Experiment registry ───────────────────────────────────────────────────────

EXPERIMENTS = {
    "Operator_41mini": {
        "dirs": [
            "mp_l1_41mini_af_op_0_49_20260317_230408",
            "mp_l1_41mini_af_op_50_99_20260317_230408",
            "mp_l9_41mini_af_op_0_14_20260317_183500",
            "mp_l9_41mini_af_op_15_29_20260317_183500",
        ],
        "tools": OPERATOR_TOOLS,
        "af_col": "AF Operator (4.1-mini)",
        "model": "41mini",
    },
    "Operator_o4mini": {
        "dirs": [
            "mp_l1_o4mini_af_op_0_49_20260317_222618",
            "mp_l1_o4mini_af_op_50_99_20260317_222618",
            "mp_l4_o4mini_af_op_0_39_20260318_103556",
            "mp_l4_o4mini_af_op_40_79_20260318_103556",
            "mp_l9_o4mini_af_op_0_14_20260317_182940",
            "mp_l9_o4mini_af_op_15_29_20260317_182940",
        ],
        "tools": OPERATOR_TOOLS,
        "af_col": "AF Operator (o4-mini)",
        "model": "o4mini",
    },
    "Pipeline_41mini": {
        "dirs": [
            "mp_l1_41mini_af_pl_0_49_20260318_002718",
            "mp_l1_41mini_af_pl_50_99_20260318_002718",
            "mp_l9_41mini_af_pl_0_14_20260317_193251",
            "mp_l9_41mini_af_pl_15_29_20260317_193251",
        ],
        "tools": PIPELINE_TOOLS,
        "af_col": "AF Pipeline (4.1-mini)",
        "model": "41mini",
    },
    "Pipeline_o4mini": {
        "dirs": [
            "mp_l1_o4mini_af_pl_0_49_20260318_020649",
            "mp_l1_o4mini_af_pl_50_99_20260318_020649",
            "mp_l9_o4mini_af_pl_0_14_20260317_195201",
            "mp_l9_o4mini_af_pl_15_29_20260317_195201",
        ],
        "tools": PIPELINE_TOOLS,
        "af_col": "AF Pipeline (o4-mini)",
        "model": "o4mini",
    },
}

# SSCoT dirs: (model, length_prefix) → list of dirs (in order; deduplicate keep=last)
SSCOT_DIRS = {
    ("41mini", "1"): ["mp_l1_41mini_sscot_0_99_20260317_174300"],
    ("41mini", "4"): ["mp_l4_41mini_sscot_0_79_20260317_174329"],
    ("41mini", "9"): ["mp_l9_41mini_sscot_0_29_20260317_174348"],
    ("o4mini",  "1"): [
        "mp_l1_o4mini_sscot_0_99_20260317_174408",
        "mp_l1_o4mini_sscot_66_99_20260318_131752",
        "mp_l1_o4mini_sscot_90_99_20260318_134324",
    ],
    ("o4mini",  "4"): ["mp_l4_o4mini_sscot_0_79_20260317_174516"],
    ("o4mini",  "9"): ["mp_l9_o4mini_sscot_0_29_20260317_174540"],
}


# ── SSCoT correctness loader ──────────────────────────────────────────────────

def load_sscot_correctness(model):
    """
    Returns two dicts keyed by case_id (e.g. '1_0'):
      pass1[case_id]    = True/False
      critique[case_id] = True/False  (True if pass-1 OR fixed by critique)
    """
    pass1   = {}
    critique_fixed = {}

    for (m, length_pfx), dirs in SSCOT_DIRS.items():
        if m != model:
            continue

        ms_rows = []
        cr_rows = []
        for d in dirs:
            p = SSCOT_BASE / d / "results"
            ms_file = p / "multi_step.csv"
            cr_file = p / "critique.csv"
            if ms_file.exists():
                ms_rows.append(pd.read_csv(ms_file))
            if cr_file.exists():
                cr_rows.append(pd.read_csv(cr_file))

        if not ms_rows:
            continue

        ms_df = pd.concat(ms_rows, ignore_index=True)
        ms_df = ms_df.rename(columns={"Length": "case_id"})
        ms_df = ms_df.drop_duplicates(subset="case_id", keep="last")

        for _, row in ms_df.iterrows():
            cid = str(row["case_id"])
            pass1[cid] = bool(row["Hard Match"])

        # critique: cases that failed pass-1 may appear here
        cr_correct = set()
        if cr_rows:
            cr_df = pd.concat(cr_rows, ignore_index=True)
            cr_df = cr_df.rename(columns={"Length": "case_id"})
            # A case is fixed by critique if any critique row for it has Hard Match=True
            for cid, grp in cr_df.groupby("case_id"):
                if grp["Hard Match"].any():
                    cr_correct.add(str(cid))

        for cid, p1 in pass1.items():
            if cid.split("_")[0] != length_pfx:
                continue
            if p1:
                critique_fixed[cid] = True
            else:
                critique_fixed[cid] = str(cid) in cr_correct

    return pass1, critique_fixed


# ── AF correctness loader ─────────────────────────────────────────────────────

def load_af_correctness(af_col):
    """
    Returns dict: {case_id: bool} for a given AF experiment column,
    merging L1 + L4 + L9 sheets from results_analysis_monteprep.xlsx.
    """
    result = {}
    xl = pd.ExcelFile(RESULTS_XL)
    for sheet in ["L1", "L4", "L9"]:
        if sheet not in xl.sheet_names:
            continue
        df = xl.parse(sheet)
        if af_col not in df.columns:
            continue
        for _, row in df.iterrows():
            cid = str(row["Case ID"])
            val = row[af_col]
            if pd.notna(val):
                result[cid] = bool(val)
    return result


# ── Parser ────────────────────────────────────────────────────────────────────

def extract_tool_counts(json_path):
    """Return {tool_name: count} from the memory field of a full_output.json."""
    with open(json_path) as f:
        data = json.load(f)
    memory = data.get("memory", {})
    counts = defaultdict(int)
    for step_val in memory.values():
        if isinstance(step_val, dict):
            tool = step_val.get("tool_name")
            if tool:
                counts[tool] += 1
    return dict(counts)


def load_experiment(exp_dirs, tools):
    rows = []
    for d in exp_dirs:
        exp_dir = AF_DIRS / d
        if not exp_dir.exists():
            print(f"  WARNING: not found: {exp_dir}")
            continue
        for case_dir in sorted(exp_dir.iterdir()):
            if not case_dir.is_dir() or not case_dir.name.startswith("case_"):
                continue
            case_id = case_dir.name.replace("case_", "")
            json_files = list(case_dir.glob("*_full_output.json"))
            if not json_files:
                print(f"  WARNING: no full_output.json in {case_dir}")
                continue
            try:
                counts = extract_tool_counts(json_files[0])
                row = {"case_id": case_id}
                for tool in tools:
                    row[tool] = counts.get(tool, 0)
                row["total_steps"] = sum(counts.get(t, 0) for t in tools)
                rows.append(row)
            except Exception as e:
                print(f"  WARNING: could not parse {json_files[0]}: {e}")
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    # Sort by case_id numerically
    df["_sort"] = df["case_id"].apply(
        lambda x: tuple(int(p) for p in str(x).split("_")) if "_" in str(x) else (0, 0)
    )
    df = df.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)
    return df


# ── Build sheets ──────────────────────────────────────────────────────────────

# Pre-load SSCoT correctness for both models
print("Loading SSCoT correctness data...")
sscot_pass1   = {}
sscot_critique = {}
for mdl in ("41mini", "o4mini"):
    p1, crit = load_sscot_correctness(mdl)
    sscot_pass1[mdl]    = p1
    sscot_critique[mdl] = crit
    print(f"  SSCoT {mdl}: {len(p1)} pass-1 entries, {len(crit)} critique entries")

sheets = {}
summary_rows = []

for exp_name, cfg in EXPERIMENTS.items():
    print(f"Loading {exp_name}...")
    df = load_experiment(cfg["dirs"], cfg["tools"])
    print(f"  {len(df)} cases")

    if not df.empty:
        model   = cfg["model"]
        af_col  = cfg["af_col"]

        # AF correctness from results_analysis_monteprep.xlsx
        af_correct_map = load_af_correctness(af_col)
        df["af_correct"] = df["case_id"].map(af_correct_map)

        # SSCoT correctness (matching model)
        df["sscot_pass1_correct"]    = df["case_id"].map(sscot_pass1.get(model, {}))
        df["sscot_critique_correct"] = df["case_id"].map(sscot_critique.get(model, {}))

    sheets[exp_name] = df

    if not df.empty:
        model_label  = "gpt-4.1-mini" if "41mini" in exp_name else "o4-mini"
        granularity  = "Operator" if "Operator" in exp_name else "Pipeline"
        for tool in cfg["tools"]:
            if tool in df.columns:
                avg   = df[tool].mean()
                total = df[tool].sum()
                if total > 0:
                    summary_rows.append({
                        "Experiment":    exp_name,
                        "Model":         model_label,
                        "Granularity":   granularity,
                        "Tool":          tool,
                        "Total Calls":   int(total),
                        "Avg per Case":  round(avg, 3),
                        "Cases with >0": int((df[tool] > 0).sum()),
                        "Cases Total":   len(df),
                    })

df_summary = pd.DataFrame(summary_rows)


# ── Write Excel ───────────────────────────────────────────────────────────────

with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
    df_summary.to_excel(writer, sheet_name="Summary", index=False)
    for sheet_name, df in sheets.items():
        if not df.empty:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    from openpyxl.utils import get_column_letter
    for sheet in writer.sheets.values():
        for col_cells in sheet.columns:
            max_len = max((len(str(c.value)) for c in col_cells if c.value), default=10)
            sheet.column_dimensions[get_column_letter(col_cells[0].column)].width = min(max_len + 4, 50)

print(f"\nDone! Saved to: {OUT}")
print("\nSummary:")
print(df_summary.to_string(index=False))
