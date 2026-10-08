import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming multiple source files)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_77/training_*.csv"
files = sorted(glob.glob(file_pattern))

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by fac_type and sum capacity
result = df_all.groupby("fac_type", as_index=False)["capacity"].sum()

# Write output with exact target schema column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)