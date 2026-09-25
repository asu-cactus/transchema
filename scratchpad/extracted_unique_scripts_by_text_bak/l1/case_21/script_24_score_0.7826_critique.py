import pandas as pd

# List all source files as per the problem statement (assuming 9 sources as hinted by 9 tuples in target)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_21/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_21/training_8.csv",
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_union = pd.concat(dfs, ignore_index=True)

# Group by Major_category and aggregate Median by mean (simple average)
result = df_union.groupby("Major_category", as_index=False)["Median"].mean()

# Write output with exact target schema and column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_21/target_multisource_mcts.csv", index=False)