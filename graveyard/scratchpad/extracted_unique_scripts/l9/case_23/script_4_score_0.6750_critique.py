import pandas as pd

# Read dimension tables (same schema)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_3.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_6.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_8.csv", index_col=0)

# Union dimension tables
df_dim = pd.concat([df2, df3, df6, df8], ignore_index=True)

# Read aspect tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_1.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_5.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_7.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_9.csv", index_col=0)

# Join unioned dimension table with each aspect table on ROW_WID using inner join
df_join = df_dim.merge(df0, on='ROW_WID', how='inner')
df_join = df_join.merge(df1, on='ROW_WID', how='inner')
df_join = df_join.merge(df4, on='ROW_WID', how='inner')
df_join = df_join.merge(df5, on='ROW_WID', how='inner')
df_join = df_join.merge(df7, on='ROW_WID', how='inner')
df_join = df_join.merge(df9, on='ROW_WID', how='inner')

# Project only the MONTHS_AGE column as per target schema
result = df_join[['MONTHS_AGE']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_23/target_multisource_mcts.csv", index=False)