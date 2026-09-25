"""
Summarize results for mcts_*_rag_ub_partial_* experiments.

Metrics per (length, sim_type):
  - n_cases      : total cases processed
  - n_correct    : number of is_correct == True
  - pct_correct  : n_correct / n_cases * 100
  - avg_cost     : mean cost (N/A rows excluded)
  - avg_latency  : mean latency_seconds (timeout rows excluded from avg)
"""
import os
import re
import pandas as pd

RESULTS_DIR = "Langraph/results_langraph"

# ── Collect all result CSVs that match the split-run naming pattern ───────────
# Pattern: mcts_l{len}_p{part}_rag_ub_partial_{opsim|pipeline}_{timestamp}
# Matches attempt 2 (_a2) split runs only.
FOLDER_RE = re.compile(
    r"^mcts_l(\d+)_p\d+_rag_ub_partial_a2_(opsim|pipeline)_\d{8}_\d{6}$"
)

records = []
for folder in sorted(os.listdir(RESULTS_DIR)):
    m = FOLDER_RE.match(folder)
    if not m:
        continue
    length, sim_type = int(m.group(1)), m.group(2)
    csv_path = os.path.join(RESULTS_DIR, folder, "results_summary.csv")
    if not os.path.exists(csv_path):
        continue
    df = pd.read_csv(csv_path)
    df["length"] = length
    df["sim_type"] = sim_type
    records.append(df)

if not records:
    print("No results found.")
    raise SystemExit

all_df = pd.concat(records, ignore_index=True)

# ── Normalise types ────────────────────────────────────────────────────────────
all_df["is_correct"] = all_df["is_correct"].astype(str).str.strip().str.lower() == "true"
all_df["cost_num"] = pd.to_numeric(all_df["cost"], errors="coerce")
all_df["latency_num"] = pd.to_numeric(all_df["latency_seconds"], errors="coerce")
# Exclude timeouts (latency == 600) from latency average
all_df["latency_for_avg"] = all_df["latency_num"].where(all_df["latency_num"] < 600)

# ── Deduplicate: if the same case_id appears in both p1 and p2 (shouldn't
#    happen with correct splits, but guard anyway) keep highest is_correct ──────
all_df = (
    all_df
    .sort_values("is_correct", ascending=False)
    .drop_duplicates(subset=["length", "sim_type", "case_id"])
    .reset_index(drop=True)
)

# ── Aggregate ─────────────────────────────────────────────────────────────────
summary = (
    all_df
    .groupby(["length", "sim_type"], sort=True)
    .agg(
        n_cases      =("case_id",        "count"),
        n_correct    =("is_correct",      "sum"),
        avg_cost     =("cost_num",        "mean"),
        avg_latency  =("latency_for_avg", "mean"),
    )
    .reset_index()
)

summary["avg_cost"]    = summary["avg_cost"].round(4)
summary["avg_latency"] = summary["avg_latency"].round(1)

# ── Pretty print ──────────────────────────────────────────────────────────────
summary_display = summary[
    ["length", "sim_type", "n_cases", "n_correct", "avg_cost", "avg_latency"]
].copy()
summary_display.columns = [
    "Length", "Sim Type", "Cases", "Correct", "Avg Cost ($)", "Avg Latency (s)"
]

print("\n===== RAG Upper-Bound Partial Reward — Results Summary =====\n")
print(summary_display.to_string(index=False))
print()
