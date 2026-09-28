import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_7/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_7/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_7/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_7/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_7/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_7/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_7/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_7/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_7/training_9.csv", index_col=0)

# Join Source9_7_0 and Source9_7_2 on all columns (inner join on all columns means intersection)
join_cols = ['admit', 'gre', 'gpa', 'prestige']
df_join = pd.merge(df0, df2, on=join_cols, how='inner', suffixes=('_0', '_2'))

# The join on all columns results in rows that are identical in both df0 and df2.
# Since the join columns are the same, the join result is effectively the intersection of df0 and df2.
# But the target schema is the same as source schema, so we can just use the join columns as the result.

# Union all source tables (including df0 and df1, df3,... df9)
df_union = pd.concat([df0, df1, df3, df4, df5, df6, df7, df8, df9], ignore_index=True)

# Combine the join result with the union result by concatenation (union)
# But the join result is a subset of df0 and df2, and df0 is included in union.
# So the join result is already included in union.
# Therefore, the final target is just the union of all source tables.

# Ensure correct dtypes as per target schema
df_final = df_union.astype({'admit': 'int64', 'gre': 'int64', 'gpa': 'float64', 'prestige': 'int64'})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_7/target_multisource_mcts.csv", index=False)