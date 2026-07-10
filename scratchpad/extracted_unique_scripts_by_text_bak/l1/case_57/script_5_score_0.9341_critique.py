import pandas as pd

# Read the single source table (if multiple, read all and union)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_57/training_0.csv", index_col=0)

# If multiple source tables existed, we would read and concat them here, e.g.:
# df1 = pd.read_csv("path_to_other_source.csv", index_col=0)
# df = pd.concat([df0, df1], ignore_index=True)
# But since only one source table is given, just use df0

df = df0

# Group by movieId and compute mean rating
result = df.groupby("movieId", as_index=False)["rating"].mean()

# Ensure correct types
result["movieId"] = result["movieId"].astype(int)
result["rating"] = result["rating"].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_57/target_multisource_mcts.csv", index=False)