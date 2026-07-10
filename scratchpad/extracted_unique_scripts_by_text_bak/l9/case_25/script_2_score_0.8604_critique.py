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

# UNION the tables with the same schema
df_union = pd.concat([df0, df1, df4, df5], ignore_index=True)

# JOIN the unioned table with all other tables on ROW_WID using inner joins
df_join = df_union.merge(df2, on='ROW_WID', how='inner') \
                  .merge(df3, on='ROW_WID', how='inner') \
                  .merge(df6, on='ROW_WID', how='inner') \
                  .merge(df7, on='ROW_WID', how='inner') \
                  .merge(df8, on='ROW_WID', how='inner') \
                  .merge(df9, on='ROW_WID', how='inner')

# Project CANCEL_DT column only, keep NaNs as is
result = df_join[['CANCEL_DT']].copy()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_25/target_multisource_mcts.csv", index=False)