import pandas as pd

# List all source files explicitly as per the naming pattern and hints
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_22/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_22/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_22/training_2.csv"
]

# Read all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# UNION all source tables
df_all = pd.concat(dfs, ignore_index=True)

# Ensure correct types
df_all = df_all.astype({'condition': 'int64', 'click': 'int64'})

# GROUP BY condition and sum clicks
result = df_all.groupby('condition', as_index=False).agg({'click': 'sum'})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)