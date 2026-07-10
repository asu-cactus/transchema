import pandas as pd

# Read all source tables with index_col=0 as per Hint 22
source_2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv', index_col=0)
source_5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv', index_col=0)
source_6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv', index_col=0)
source_8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv', index_col=0)

source_0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv', index_col=0)
source_1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv', index_col=0)
source_3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv', index_col=0)
source_4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv', index_col=0)
source_7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv', index_col=0)
source_9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv', index_col=0)

# UNION dimension tables (all have same schema)
dim_union = pd.concat([source_2, source_5, source_6, source_8], ignore_index=True)

# Join dimension union with other aspect tables on ROW_WID
df = dim_union.merge(source_0, on='ROW_WID', how='inner')
df = df.merge(source_1, on='ROW_WID', how='inner')
df = df.merge(source_3, on='ROW_WID', how='inner')
df = df.merge(source_4, on='ROW_WID', how='inner')
df = df.merge(source_7, on='ROW_WID', how='inner')
df = df.merge(source_9, on='ROW_WID', how='inner')

# Project only the target column KEYWORDS_NUM
result = df[['KEYWORDS_NUM']]

# Write to output CSV
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv', index=False)