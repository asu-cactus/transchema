import pandas as pd

# List all source files (assuming 5 source files named training_0.csv to training_4.csv)
file_paths = [
    "autopipeline-benchmarks/github-pipelines/length1_4/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_4.csv"
]

# Read and union all source tables
dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'fname' and count occurrences
result = df_all.groupby("fname", as_index=False).agg(count_of_obs=("fname", "count"))

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts.csv", index=False)