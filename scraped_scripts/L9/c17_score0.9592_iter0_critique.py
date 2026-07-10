import pandas as pd

# List of source file paths and their corresponding table names
source_files = [
    "autopipeline-benchmarks/github-pipelines/length9_17/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_11.csv",
]

# Read all source tables with index_col=0 to ignore the numerical index column
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Concatenate all dataframes (UNION)
result = pd.concat(dfs, ignore_index=True)

# Write the final output to the target file
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_17/target_multisource_mcts.csv", index=False)