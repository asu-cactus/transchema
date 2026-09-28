import pandas as pd
import glob

# Read all source files matching the pattern
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_80/training_*.csv"
files = glob.glob(file_pattern)

# Read and concatenate all source tables
dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by movieId and compute average rating
result = df_all.groupby("movieId", as_index=False)["rating"].mean()

# Ensure column names exactly as target schema
result.columns = ["movieId", "rating"]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)