import pandas as pd

# List all source file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length9_45/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_45/training_21.csv",
]

# Read all source tables with index_col=0 to ignore the numerical index column
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# UNION all source tables (concatenate vertically)
result = pd.concat(dfs, ignore_index=True)

# Write the result to the target file
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_45/target_multisource_mcts.csv", index=False)