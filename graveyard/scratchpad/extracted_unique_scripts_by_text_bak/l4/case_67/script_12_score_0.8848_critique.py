import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming multiple source files)
# Since only one source file is given explicitly, we read only that.
# If more source files exist, they should be added here.
# For demonstration, we only read the given source file.

source_files = [
    "autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv"
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by "Batsman on strike" and aggregate
grouped = df_all.groupby("Batsman on strike").agg({
    "overs": "max",
    "runs scored": "sum",
    "extras": "sum"
}).reset_index()

# Cast columns to correct types
grouped["overs"] = grouped["overs"].astype(float)
grouped["runs scored"] = grouped["runs scored"].astype(int)
grouped["extras"] = grouped["extras"].astype(int)

# Reorder columns to match target schema exactly
grouped = grouped[["Batsman on strike", "overs", "runs scored", "extras"]]

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)