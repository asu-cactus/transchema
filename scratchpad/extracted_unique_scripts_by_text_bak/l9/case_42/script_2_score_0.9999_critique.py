import pandas as pd

# List all source file paths
source_files = [
    f"autopipeline-benchmarks/github-pipelines/length9_42/training_{i}.csv" for i in range(222)
]

# Read all source tables with index_col=0 to ignore the numerical index column
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Union all source tables by concatenation
result = pd.concat(dfs, ignore_index=True)

# Write the final output with exact column names as in target schema
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_42/target_multisource_mcts.csv", index=False)