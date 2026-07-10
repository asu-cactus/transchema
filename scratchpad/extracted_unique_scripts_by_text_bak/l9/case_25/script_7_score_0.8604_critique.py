import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_9.csv", index_col=0)

# UNION the four tables with the same schema
union_df = pd.concat([df0, df1, df4, df5], ignore_index=True)

# Join with other tables on ROW_WID (inner join to keep only matching rows)
joined_1 = union_df.merge(df2, on='ROW_WID', how='inner')
joined_2 = joined_1.merge(df3, on='ROW_WID', how='inner')
joined_3 = joined_2.merge(df6, on='ROW_WID', how='inner')
joined_4 = joined_3.merge(df7, on='ROW_WID', how='inner')
joined_5 = joined_4.merge(df8, on='ROW_WID', how='inner')
joined_6 = joined_5.merge(df9, on='ROW_WID', how='inner')

# Output only CANCEL_DT column as in target schema, preserving NaNs
joined_6[['CANCEL_DT']].to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)