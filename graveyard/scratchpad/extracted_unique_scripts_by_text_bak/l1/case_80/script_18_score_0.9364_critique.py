import pandas as pd
import glob

# Read all source CSV files matching the pattern
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_80/training_*.csv"
files = glob.glob(file_pattern)

# Read and concatenate all source tables (union)
df_list = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(df_list, ignore_index=True)

# Group by movieId and aggregate mean rating
result = df_all.groupby("movieId", as_index=False).agg(rating=("rating", "mean"))

# Write output with exact column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)