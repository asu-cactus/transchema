import pandas as pd

# List all source files (assuming multiple)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_29/training_1.csv",
    # add all source files here
]

# Read and union all source tables
df_list = [pd.read_csv(f, index_col=0) for f in source_files]
df_union = pd.concat(df_list, ignore_index=True)

# Group by Gender and count Purchase ID
df_grouped = df_union.groupby('Gender', as_index=False).agg({'Purchase ID': 'count'})

# Rename count column to '0'
df_grouped.rename(columns={'Purchase ID': '0'}, inplace=True)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)