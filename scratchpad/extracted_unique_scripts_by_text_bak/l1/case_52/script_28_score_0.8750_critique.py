import pandas as pd

# List all source files as per the naming pattern and hints (assuming 10 source files)
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

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_union = pd.concat(dfs, ignore_index=True)

# Group by 'condition' and sum 'click'
pivot_df = df_union.groupby('condition', as_index=False)['click'].sum()

# Rename columns to match target schema
pivot_df.columns = ['condition', '0']

# Ensure correct types
pivot_df['condition'] = pivot_df['condition'].astype(int)
pivot_df['0'] = pivot_df['0'].astype(int)

# Write output
pivot_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)