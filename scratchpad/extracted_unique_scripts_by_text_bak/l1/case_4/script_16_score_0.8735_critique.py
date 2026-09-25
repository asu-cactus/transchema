import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming 4 source files as per naming convention)
file_paths = sorted(glob.glob("autopipeline-benchmarks/github-pipelines/length1_4/training_*.csv"))

# Read all source tables into a list of dataframes
dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]

# Union all source tables (concatenate)
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'fname' and count observations
result = df_all.groupby("fname").size().reset_index(name="count_of_obs")

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts.csv", index=False)