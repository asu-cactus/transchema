import pandas as pd
import glob

# Read all source CSV files matching the pattern
file_paths = glob.glob("autopipeline-benchmarks/github-pipelines/length1_92/training_*.csv")

# Read all source tables with index_col=0
dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]

# Concatenate all source tables (UNION)
result = pd.concat(dfs, ignore_index=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)