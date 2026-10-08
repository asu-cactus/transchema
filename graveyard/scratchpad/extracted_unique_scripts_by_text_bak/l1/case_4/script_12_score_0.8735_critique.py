import pandas as pd

# List all source files (assuming 4 source files as per naming pattern)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_4/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_3.csv"
]

# Read all source files with index_col=0 and concatenate (UNION)
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'fname' and count observations
result = df_all.groupby("fname").size().reset_index(name="count_of_obs")

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts.csv", index=False)