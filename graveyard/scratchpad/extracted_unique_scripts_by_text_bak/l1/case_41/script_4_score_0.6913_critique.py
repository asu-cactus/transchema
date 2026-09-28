import pandas as pd

# List all source files (assuming 3 source files for example)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_41/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_41/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_41/training_2.csv"
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by zipcode and aggregate sums
agg_df = df_all.groupby("zipcode", as_index=False).agg({
    "AGI_STUB": "sum",
    "N1": "sum",
    "A00100": "sum"
})

# Ensure correct dtypes matching target schema
agg_df = agg_df.astype({
    "zipcode": "int64",
    "AGI_STUB": "int64",
    "N1": "int64",
    "A00100": "int64"
})

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts.csv", index=False)