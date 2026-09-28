import pandas as pd
import glob

# List all source CSV files
source_files = [
    f"autopipeline-benchmarks/github-pipelines/length9_41/training_{i}.csv"
    for i in range(222)
]

# Read and concatenate all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by the key columns to remove duplicates if any
df_final = df_all.groupby(['Baker', 'Age', 'Occupation', 'Hometown'], dropna=False, as_index=False).first()

# Keep Links column as is (no aggregation)
# The .first() keeps the first non-null Links value per group

# Write to target file
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_41/target_multisource_mcts.csv", index=False)