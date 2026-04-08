"""
analyze_intermat_variability.py

Reads the 3 intermediate-materialization multi-step+critique runs and produces
intermat_variability.xlsx with two sheets:

  Sheet 1 — Raw Data   : per-case Hard Match, Cost, Latency for MS and Critique
                         across all 3 runs, plus combined totals.
  Sheet 2 — Variability: final correctness per run (MS OR any Critique Hard Match),
                         plus summary:
                           - Cases correct at least once  (>=1 of 3)
                           - Cases correct at least twice (>=2 of 3)
                           - Cases correct in all 3 runs  (3 of 3)

Column mapping (CSV headers are mislabeled):
  multi_step.csv : Length, Hard Match, Soft Match (=cost $), Soft Acc (=latency s), ...
  critique.csv   : Length, Critique Type, Hard Match, Soft Match (=cost $), Soft Acc (=latency s), ...
"""

import pandas as pd
from pathlib import Path

ROOT    = Path(__file__).resolve().parent
MS_BASE = ROOT / "logs-auto-suggest-llm-21-04"
OUT     = ROOT / "intermat_variability.xlsx"

RUN_DIRS = [
    "intermat_30cases_ms_20260406_163632",
    "intermat_30cases_ms_20260406_175135",
    "intermat_30cases_ms_20260406_190837",
]
RUN_LABELS = ["Run 1", "Run 2", "Run 3"]


def to_bool(series):
    return series.map(lambda v: True if str(v).strip().lower() in ("true", "1") else False)


def load_run(run_dir: str):
    ms_path   = MS_BASE / run_dir / "results" / "multi_step.csv"
    crit_path = MS_BASE / run_dir / "results" / "critique.csv"

    # ── Multi-step ────────────────────────────────────────────────────────────
    ms = pd.read_csv(ms_path)
    ms = ms.rename(columns={ms.columns[0]: "Case"})
    ms["Case"]       = ms["Case"].astype(str)
    ms["MS Correct"] = to_bool(ms["Hard Match"])
    ms["MS Cost"]    = pd.to_numeric(ms["Soft Match"], errors="coerce").fillna(0)   # small decimals
    ms["MS Latency"] = pd.to_numeric(ms["Soft Acc"],   errors="coerce").fillna(0)   # large seconds

    ms = ms[["Case", "MS Correct", "MS Cost", "MS Latency"]]

    # ── Critique ──────────────────────────────────────────────────────────────
    crit = pd.read_csv(crit_path)
    crit = crit.rename(columns={crit.columns[0]: "Case"})
    crit["Case"]          = crit["Case"].astype(str)
    crit["Crit Correct"]  = to_bool(crit["Hard Match"])
    crit["Crit Cost"]     = pd.to_numeric(crit["Soft Match"], errors="coerce").fillna(0)
    crit["Crit Latency"]  = pd.to_numeric(crit["Soft Acc"],   errors="coerce").fillna(0)
    crit["Crit Types"]    = crit["Critique Type"].astype(str)

    # Aggregate per case: any correct, sum cost/latency, list types tried
    crit_agg = (
        crit.groupby("Case")
        .agg(
            Crit_Correct  = ("Crit Correct",  "any"),
            Crit_Cost     = ("Crit Cost",      "sum"),
            Crit_Latency  = ("Crit Latency",   "sum"),
            Crit_Types    = ("Crit Types",     lambda x: ", ".join(x)),
        )
        .reset_index()
    )

    # ── Merge and compute totals ──────────────────────────────────────────────
    merged = ms.merge(crit_agg, on="Case", how="left")
    merged["Crit_Correct"] = merged["Crit_Correct"].fillna(False)
    merged["Crit_Cost"]    = merged["Crit_Cost"].fillna(0)
    merged["Crit_Latency"] = merged["Crit_Latency"].fillna(0)
    merged["Crit_Types"]   = merged["Crit_Types"].fillna("")

    merged["Final Correct"]   = merged["MS Correct"] | merged["Crit_Correct"]
    merged["Total Cost ($)"]  = merged["MS Cost"]    + merged["Crit_Cost"]
    merged["Total Latency (s)"] = merged["MS Latency"] + merged["Crit_Latency"]

    return merged


# ── Load all runs ─────────────────────────────────────────────────────────────

runs = {label: load_run(d) for label, d in zip(RUN_LABELS, RUN_DIRS)}


# ── Sheet 1: Raw Data ─────────────────────────────────────────────────────────

def prefix_cols(df, label):
    """Rename all columns except Case with a run prefix."""
    return df.rename(columns={c: f"{label} | {c}" for c in df.columns if c != "Case"})

raw = prefix_cols(runs["Run 1"], "Run 1")
for label in ["Run 2", "Run 3"]:
    raw = raw.merge(prefix_cols(runs[label], label), on="Case", how="outer")

raw = raw.sort_values("Case").reset_index(drop=True)

# Reorder columns: Case, then grouped by run
ordered_cols = ["Case"]
fields = ["MS Correct", "MS Cost", "MS Latency",
          "Crit_Correct", "Crit_Cost", "Crit_Latency", "Crit_Types",
          "Final Correct", "Total Cost ($)", "Total Latency (s)"]
for label in RUN_LABELS:
    for f in fields:
        col = f"{label} | {f}"
        if col in raw.columns:
            ordered_cols.append(col)

raw = raw[ordered_cols]


# ── Sheet 2: Variability ──────────────────────────────────────────────────────

truth = runs["Run 1"][["Case", "MS Correct", "Crit_Correct", "Final Correct"]].rename(columns={
    "MS Correct":    "Run 1 MS",
    "Crit_Correct":  "Run 1 Crit",
    "Final Correct": "Run 1 Final",
})
for label in ["Run 2", "Run 3"]:
    t = runs[label][["Case", "MS Correct", "Crit_Correct", "Final Correct"]].rename(columns={
        "MS Correct":    f"{label} MS",
        "Crit_Correct":  f"{label} Crit",
        "Final Correct": f"{label} Final",
    })
    truth = truth.merge(t, on="Case", how="outer")

truth = truth.sort_values("Case").reset_index(drop=True)

final_cols = ["Run 1 Final", "Run 2 Final", "Run 3 Final"]
truth["Correct Count"] = truth[final_cols].sum(axis=1)
truth["Correct ≥1"]    = truth["Correct Count"] >= 1
truth["Correct ≥2"]    = truth["Correct Count"] >= 2
truth["Correct All 3"] = truth["Correct Count"] == 3

n_cases = len(truth)
summary = pd.DataFrame([
    {},
    {"Case": "— SUMMARY —"},
    {"Case": "Cases correct ≥1",    "Run 1 MS": truth["Correct ≥1"].sum()},
    {"Case": "Cases correct ≥2",    "Run 1 MS": truth["Correct ≥2"].sum()},
    {"Case": "Cases correct all 3", "Run 1 MS": truth["Correct All 3"].sum()},
    {"Case": "Total cases",         "Run 1 MS": n_cases},
])
variability = pd.concat([truth, summary], ignore_index=True)


# ── Write Excel ───────────────────────────────────────────────────────────────

with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
    raw.to_excel(writer, sheet_name="Raw Data", index=False)
    variability.to_excel(writer, sheet_name="Variability", index=False)

    for sheet_name in ["Raw Data", "Variability"]:
        ws = writer.sheets[sheet_name]
        for col_cells in ws.columns:
            max_len = max(
                (len(str(cell.value)) if cell.value is not None else 0)
                for cell in col_cells
            )
            ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 4, 60)

print(f"Written → {OUT}")
print(f"\nVariability summary (MS OR Critique):")
print(f"  Correct ≥1 : {truth['Correct ≥1'].sum()} / {n_cases}")
print(f"  Correct ≥2 : {truth['Correct ≥2'].sum()} / {n_cases}")
print(f"  Correct all: {truth['Correct All 3'].sum()} / {n_cases}")
