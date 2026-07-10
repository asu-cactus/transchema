import pandas as pd

# List all source files (assuming 5 source files with similar schema as per naming pattern)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_77/training_4.csv",
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by fac_type and sum capacity
result = df_all.groupby("fac_type", as_index=False)["capacity"].sum()

# Ensure capacity is integer type
result["capacity"] = result["capacity"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)