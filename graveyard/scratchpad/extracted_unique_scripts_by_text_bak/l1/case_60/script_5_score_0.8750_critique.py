import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming 10 files as example)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_60/training_*.csv"
files = sorted(glob.glob(file_pattern))

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

# Filter rows where type == "Urban"
df_filtered = df_all[df_all["type"] == "Urban"]

# Group by 'type' and sum 'driver_count'
result = df_filtered.groupby("type", as_index=False)["driver_count"].sum()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)