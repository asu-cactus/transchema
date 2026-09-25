import pandas as pd

# List all source file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length9_53/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_53/training_14.csv",
]

# Read all sources into a list of dataframes
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Concatenate all dataframes (UNION)
result = pd.concat(dfs, ignore_index=True)

# Ensure column name and type matches target schema
result = result.astype({"addr_state": "Int64"})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_53/target_multisource_mcts.csv", index=False)