import pandas as pd

# File paths for all source tables
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

# Read all source tables with index_col=0 to ignore the numerical index column
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Concatenate all dataframes (UNION)
result = pd.concat(dfs, ignore_index=True)

# Ensure columns are exactly as target schema (same as source schema)
# The source schemas are identical and match target schema column names

# Write the result to the target file
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_96/target_multisource_mcts.csv", index=False)