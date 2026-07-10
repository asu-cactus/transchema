import pandas as pd

# Read dimension tables with same schema
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_1.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_5.csv", index_col=0)

# Union dimension tables
unioned_dim = pd.concat([df0, df1, df4, df5], ignore_index=True)

# Read aspect tables
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_3.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_25/training_9.csv", index_col=0)

# Join unioned_dim with each aspect table on ROW_WID using inner join
result = unioned_dim.merge(df2, on='ROW_WID', how='inner')
result = result.merge(df3, on='ROW_WID', how='inner')
result = result.merge(df6, on='ROW_WID', how='inner')
result = result.merge(df7, on='ROW_WID', how='inner')
result = result.merge(df8, on='ROW_WID', how='inner')
result = result.merge(df9, on='ROW_WID', how='inner')

# Project CANCEL_DT column and convert to string type as in target
result = result[['CANCEL_DT']].copy()
result['CANCEL_DT'] = result['CANCEL_DT'].astype('string')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)