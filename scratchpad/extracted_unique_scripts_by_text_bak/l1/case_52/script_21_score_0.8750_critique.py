import pandas as pd

# List all source files as per the problem statement (assuming 10 source files named accordingly)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_9.csv",
]

# Read all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# UNION all source tables
df_union = pd.concat(dfs, ignore_index=True)

# GROUP BY 'condition' and sum 'click'
df_grouped = df_union.groupby('condition', as_index=False)['click'].sum()

# Rename columns to match target schema
df_grouped.columns = ['condition', '0']

# Ensure correct types
df_grouped['condition'] = df_grouped['condition'].astype(int)
df_grouped['0'] = df_grouped['0'].astype(int)

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)