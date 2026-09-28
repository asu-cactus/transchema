import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_4.csv", index_col=0)

# Join df0 and df1 on all columns (exact match rows)
join_cols = ['Year', 'Category', 'Nominee', 'Movie', 'Winner']
df0_1_joined = pd.merge(df0, df1, on=join_cols, how='inner', suffixes=('_0', '_1'))

# The join produces rows that exist in both df0 and df1 exactly on all columns.
# But the target schema is just the 5 columns, so we keep only those columns.
df0_1_joined = df0_1_joined[join_cols]

# Union all source tables (including df0 and df1 again)
df_union = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# The target schema is ['Year', 'Category', 'Nominee', 'Movie', 'Winner'] all strings.
# Ensure all columns are string type
for col in join_cols:
    df_union[col] = df_union[col].astype(str)

# Save the result
df_union.to_csv("autopipeline-benchmarks/github-pipelines/length4_65/target_multisource_mcts.csv", index=False)