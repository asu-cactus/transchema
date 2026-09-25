import pandas as pd

# List all source files (assuming 5 source files named training_0.csv to training_4.csv)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_80/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_4.csv"
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by movieId and compute mean rating
result = df_all.groupby("movieId", as_index=False)["rating"].mean()

# Ensure correct types
result["movieId"] = result["movieId"].astype(int)
result["rating"] = result["rating"].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)