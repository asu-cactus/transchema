import pandas as pd

# List all source files (assuming 5 source files as an example)
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

# Group by movieId and compute average rating
result = df_all.groupby("movieId", as_index=False)["rating"].mean()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)