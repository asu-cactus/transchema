import pandas as pd

src_paths = {
    "Source9_98_0": "autopipeline-benchmarks/github-pipelines/length9_98/training_0.csv",
    "Source9_98_1": "autopipeline-benchmarks/github-pipelines/length9_98/training_1.csv",
    "Source9_98_2": "autopipeline-benchmarks/github-pipelines/length9_98/training_2.csv",
    "Source9_98_3": "autopipeline-benchmarks/github-pipelines/length9_98/training_3.csv",
    "Source9_98_4": "autopipeline-benchmarks/github-pipelines/length9_98/training_4.csv",
    "Source9_98_5": "autopipeline-benchmarks/github-pipelines/length9_98/training_5.csv",
    "Source9_98_6": "autopipeline-benchmarks/github-pipelines/length9_98/training_6.csv",
    "Source9_98_7": "autopipeline-benchmarks/github-pipelines/length9_98/training_7.csv",
    "Source9_98_8": "autopipeline-benchmarks/github-pipelines/length9_98/training_8.csv",
    "Source9_98_9": "autopipeline-benchmarks/github-pipelines/length9_98/training_9.csv",
}

df_0 = pd.read_csv(src_paths["Source9_98_0"], index_col=0)
df_4 = pd.read_csv(src_paths["Source9_98_4"], index_col=0)

join_cols = ['admit', 'gre', 'gpa', 'prestige']
df_joined = pd.merge(df_0, df_4, on=join_cols, how='inner', suffixes=('_0', '_4'))

# The join above will produce only rows that are exactly the same in both tables on all columns.
# This is a very restrictive join and likely results in a subset of df_0 or df_4.
# However, the partial plan suggests this join as first step.

# Next, union all source tables except Source9_98_4 (already joined with Source9_98_0)
# But the partial plan union includes Source9_98_0 and excludes Source9_98_4.
# So we union all except Source9_98_4.

dfs_to_union = []
for i in range(10):
    if i == 4:
        continue
    df = pd.read_csv(src_paths[f"Source9_98_{i}"], index_col=0)
    dfs_to_union.append(df)

df_union = pd.concat(dfs_to_union, ignore_index=True)

# The target schema is ['admit': int, 'gre': int, 'gpa': float, 'prestige': int]
# Ensure dtypes match target schema
df_union = df_union.astype({'admit': 'int64', 'gre': 'int64', 'gpa': 'float64', 'prestige': 'int64'})

# Save to target path
df_union.to_csv("autopipeline-benchmarks/github-pipelines/length9_98/target_multisource_mcts.csv", index=False)