import pandas as pd

# List all source files (assuming 8 source files as typical for this benchmark)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_21/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_7.csv"
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by Major_category and compute mean of Median
result = df_all.groupby("Major_category", as_index=False)["Median"].mean()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_21/target_multisource_mcts.csv", index=False)