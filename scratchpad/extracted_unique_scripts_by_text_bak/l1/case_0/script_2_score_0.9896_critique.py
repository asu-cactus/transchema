import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming multiple source files exist)
# The problem states only one source file explicitly, but instructions require all source tables used.
# So we glob all CSV files in the directory matching the pattern "training_*.csv"
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_0/training_*.csv"
files = glob.glob(file_pattern)

# Read and concatenate all source tables
dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'State' and compute mean of 'AverageTemperature'
result = df_all.groupby("State", as_index=False)["AverageTemperature"].mean()

# Rename columns to match target schema exactly
result.columns = ["State", "AverageTemperature"]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts.csv", index=False)