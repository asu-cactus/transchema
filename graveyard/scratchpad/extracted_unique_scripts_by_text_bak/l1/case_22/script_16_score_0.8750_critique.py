import pandas as pd
import glob

# Read all source CSV files matching the pattern (all source tables)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_22/training_*.csv"
all_files = glob.glob(file_pattern)

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in all_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'condition' and sum 'click'
result = df_all.groupby("condition", as_index=False)["click"].sum()

# Ensure correct types
result["condition"] = result["condition"].astype(int)
result["click"] = result["click"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)