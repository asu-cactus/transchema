import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_31/training_9.csv", index_col=0)

# UNION the four large tables with the same schema
df_union = pd.concat([df0, df1, df3, df5], ignore_index=True)

# JOIN the unioned table with all other tables on ROW_WID
df_join = df_union.merge(df2, on='ROW_WID', how='inner')
df_join = df_join.merge(df4, on='ROW_WID', how='inner')
df_join = df_join.merge(df6, on='ROW_WID', how='inner')
df_join = df_join.merge(df7, on='ROW_WID', how='inner')
df_join = df_join.merge(df8, on='ROW_WID', how='inner')
df_join = df_join.merge(df9, on='ROW_WID', how='inner')

# Project only the HOME_PASSED column as per target schema
result = df_join[['HOME_PASSED']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)