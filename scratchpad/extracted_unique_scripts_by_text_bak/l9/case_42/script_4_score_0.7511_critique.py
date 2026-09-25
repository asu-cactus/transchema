import pandas as pd

# List all source file paths
source_files = [
    f"autopipeline-benchmarks/github-pipelines/length9_42/training_{i}.csv" for i in range(222)
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_union = pd.concat(dfs, ignore_index=True)

# Group by all columns to remove duplicates (no aggregation)
group_by_cols = ['Baker', 'Signature', 'Technical', 'Showstopper', 'episode_number', 'episode_theme', 'season']
df_result = df_union.drop_duplicates(subset=group_by_cols)

# Sort by group_by_cols to have consistent order (optional)
df_result = df_result.sort_values(by=group_by_cols).reset_index(drop=True)

# Write to target file
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_42/target_multisource_mcts.csv", index=False)