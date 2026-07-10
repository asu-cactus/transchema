import pandas as pd

# List all source file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length9_41/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_41/training_21.csv",
]

# Note: The problem states 222 sources (Source9_41_0 to Source9_41_221)
# For brevity, only 22 are listed here. In actual code, list all 222 source files.

# To handle all sources, generate the list programmatically:
source_files = [
    f"autopipeline-benchmarks/github-pipelines/length9_41/training_{i}.csv"
    for i in range(222)
]

# Read all source tables with index_col=0 to ignore the first index column
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# UNION all source tables by concatenation
result = pd.concat(dfs, ignore_index=True)

# Write the final output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_41/target_multisource_mcts.csv", index=False)