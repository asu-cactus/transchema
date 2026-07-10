import pandas as pd
import glob

# Read all source CSV files matching the pattern
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_24/training_*.csv"
files = glob.glob(file_pattern)

# Read and concatenate all source tables
dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'condition' and sum 'click'
result = df_all.groupby("condition", as_index=False)["click"].sum()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_24/target_multisource_mcts.csv", index=False)