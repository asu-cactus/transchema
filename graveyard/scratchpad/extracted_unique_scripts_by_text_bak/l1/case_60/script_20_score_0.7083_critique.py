import pandas as pd

# List all source files (assuming 10 source files as an example)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_60/training_9.csv",
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
union_df = pd.concat(dfs, ignore_index=True)

# Group by 'type' and sum 'driver_count'
result = union_df.groupby("type", as_index=False)["driver_count"].sum()

# Ensure correct types
result["type"] = result["type"].astype(str)
result["driver_count"] = result["driver_count"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)