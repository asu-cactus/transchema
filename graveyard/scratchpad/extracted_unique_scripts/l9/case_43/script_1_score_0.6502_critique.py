import pandas as pd

# List all source file paths and their variable names
source_files = [
    "autopipeline-benchmarks/github-pipelines/length9_43/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length9_43/training_29.csv",
]

# Read all source tables with index_col=0 to ignore the first index column
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Union all source tables (concatenate)
result = pd.concat(dfs, ignore_index=True)

# Write the final output to the target file
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_43/target_multisource_mcts.csv", index=False)