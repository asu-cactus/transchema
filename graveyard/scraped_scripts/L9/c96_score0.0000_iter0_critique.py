import pandas as pd

# Read all source CSV files with index_col=0 as per hint 22
source_files = [
    "autopipeline-benchmarks/github-pipelines/length9_96/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_96/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_96/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_96/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_96/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_96/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_96/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_96/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_96/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_96/training_9.csv",
]

# Load all sources into a list of DataFrames
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Concatenate all dataframes (UNION)
result = pd.concat(dfs, ignore_index=True)

# Write the result to the target CSV file
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_96/target_multisource_mcts.csv", index=False)