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

# UNION the four source tables with the same schema
unioned = pd.concat([df0, df1, df3, df5], ignore_index=True)

# Join all other tables on ROW_WID
joined = unioned.merge(df2, on='ROW_WID', how='left') \
                .merge(df4, on='ROW_WID', how='left') \
                .merge(df6, on='ROW_WID', how='left') \
                .merge(df7, on='ROW_WID', how='left') \
                .merge(df8, on='ROW_WID', how='left') \
                .merge(df9, on='ROW_WID', how='left')

# Group by ROW_WID and sum HOME_PASSED
result = joined.groupby('ROW_WID', as_index=False)['HOME_PASSED'].sum()

# Project only HOME_PASSED column as per target schema
result = result[['HOME_PASSED']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_31/target_multisource_mcts.csv", index=False)