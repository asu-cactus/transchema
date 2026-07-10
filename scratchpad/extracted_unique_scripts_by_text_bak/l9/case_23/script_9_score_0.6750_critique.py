import pandas as pd

# Read dimension tables with same schema
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_3.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_6.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_8.csv", index_col=0)

# Union dimension tables
union_dim = pd.concat([df2, df3, df6, df8], ignore_index=True)

# Read aspect tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_1.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_5.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_7.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_9.csv", index_col=0)

# Join unioned dimension table with each aspect table on ROW_WID using inner join
joined_1 = pd.merge(union_dim, df0, on='ROW_WID', how='inner')
joined_2 = pd.merge(joined_1, df1, on='ROW_WID', how='inner')
joined_3 = pd.merge(joined_2, df4, on='ROW_WID', how='inner')
joined_4 = pd.merge(joined_3, df5, on='ROW_WID', how='inner')
joined_5 = pd.merge(joined_4, df7, on='ROW_WID', how='inner')
joined_all = pd.merge(joined_5, df9, on='ROW_WID', how='inner')

# Group by ROW_WID and aggregate MONTHS_AGE by mean
grouped = joined_all.groupby('ROW_WID', as_index=False).agg({'MONTHS_AGE': 'mean'})

# Project MONTHS_AGE only
result = grouped[['MONTHS_AGE']].copy()
result['MONTHS_AGE'] = result['MONTHS_AGE'].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_23/target_multisource_mcts.csv", index=False)