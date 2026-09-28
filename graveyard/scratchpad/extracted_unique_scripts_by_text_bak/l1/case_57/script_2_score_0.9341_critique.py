import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming 5 source files as example)
file_paths = sorted(glob.glob("autopipeline-benchmarks/github-pipelines/length1_57/training_*.csv"))

dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]

# UNION all source tables by concatenation
df_all = pd.concat(dfs, ignore_index=True)

# GROUP BY movieId and aggregate rating by mean
result = df_all.groupby("movieId", as_index=False)["rating"].mean()

# Ensure correct types
result["movieId"] = result["movieId"].astype(int)
result["rating"] = result["rating"].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_57/target_multisource_mcts.csv", index=False)