import pandas as pd

# File paths for all sources
file_paths = [
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

# Read all source tables with index_col=0 as per hint 22
dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]

# Concatenate all dataframes vertically (UNION)
result = pd.concat(dfs, ignore_index=True)

# Write to target file with exact column names preserved
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_96/target_multisource_mcts.csv", index=False)