import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming 4 source files as example)
file_paths = sorted(glob.glob("autopipeline-benchmarks/github-pipelines/length4_67/training_*.csv"))

# Read and union all source tables
dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]
df_all = pd.concat(dfs, ignore_index=True)

# Group by "Batsman on strike" and aggregate
agg_df = df_all.groupby("Batsman on strike").agg({
    "overs": "max",
    "runs scored": "sum",
    "extras": "sum"
}).reset_index()

# Ensure correct dtypes as per target schema
agg_df["overs"] = agg_df["overs"].astype(float)
agg_df["runs scored"] = agg_df["runs scored"].astype(int)
agg_df["extras"] = agg_df["extras"].astype(int)

# Reorder columns to match target schema exactly
agg_df = agg_df[["Batsman on strike", "overs", "runs scored", "extras"]]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)