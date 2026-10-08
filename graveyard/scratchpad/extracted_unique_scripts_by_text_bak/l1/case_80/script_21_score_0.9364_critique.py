import pandas as pd
import glob

# Read all source files matching the pattern (assuming all source files are named similarly)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_80/training_*.csv"
file_list = sorted(glob.glob(file_pattern))

# Read all source tables into a list of dataframes
dfs = [pd.read_csv(f, index_col=0) for f in file_list]

# Union all source tables
df_union = pd.concat(dfs, ignore_index=True)

# Group by movieId and aggregate by mean rating
result = df_union.groupby('movieId', as_index=False)['rating'].mean()

# Ensure correct types
result['movieId'] = result['movieId'].astype(int)
result['rating'] = result['rating'].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)