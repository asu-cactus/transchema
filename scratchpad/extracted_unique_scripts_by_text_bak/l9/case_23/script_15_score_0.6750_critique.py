import pandas as pd

# Read all source CSVs with index_col=0
source_0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_23/training_0.csv', index_col=0)
source_1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_23/training_1.csv', index_col=0)
source_2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_23/training_2.csv', index_col=0)
source_3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_23/training_3.csv', index_col=0)
source_4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_23/training_4.csv', index_col=0)
source_5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_23/training_5.csv', index_col=0)
source_6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_23/training_6.csv', index_col=0)
source_7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_23/training_7.csv', index_col=0)
source_8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_23/training_8.csv', index_col=0)
source_9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_23/training_9.csv', index_col=0)

# UNION dimension tables with same schema
dim_union = pd.concat([source_2, source_3, source_6, source_8], ignore_index=True)

# Join dimension union with all aspect tables on ROW_WID
# Start with dim_union and source_0
df = pd.merge(dim_union, source_0, on='ROW_WID', how='inner')

# Join with source_1
df = pd.merge(df, source_1, on='ROW_WID', how='inner')

# Join with source_4
df = pd.merge(df, source_4, on='ROW_WID', how='inner')

# Join with source_5
df = pd.merge(df, source_5, on='ROW_WID', how='inner')

# Join with source_7
df = pd.merge(df, source_7, on='ROW_WID', how='inner')

# Join with source_9
df = pd.merge(df, source_9, on='ROW_WID', how='inner')

# Project only MONTHS_AGE column as per target schema
result = df[['MONTHS_AGE']]

# Write output CSV without index
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_23/target_multisource_mcts.csv', index=False)