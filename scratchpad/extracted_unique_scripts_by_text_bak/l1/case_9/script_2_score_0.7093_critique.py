import pandas as pd

# List all source files (assuming 5 source files as per typical naming)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_9/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_9/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_9/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_9/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_9/training_4.csv"
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by zipcode and aggregate sums
grouped = df_all.groupby("zipcode", as_index=False).agg({
    "AGI_STUB": "sum",
    "N1": "sum",
    "A00100": "sum"
})

# Cast to int64 to match target schema
grouped = grouped.astype({
    "zipcode": "int64",
    "AGI_STUB": "int64",
    "N1": "int64",
    "A00100": "int64"
})

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts.csv", index=False)