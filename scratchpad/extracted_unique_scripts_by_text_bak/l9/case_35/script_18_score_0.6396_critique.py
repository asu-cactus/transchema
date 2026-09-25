import pandas as pd

# Read source tables
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_3.csv', index_col=0)
source4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv', index_col=0)
source5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_5.csv', index_col=0)
source6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_6.csv', index_col=0)
source7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_7.csv', index_col=0)
source8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv', index_col=0)
source9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv', index_col=0)

# UNION dimension tables
dim_union = pd.concat([source0, source1, source8, source9], ignore_index=True)

# Join with aspect tables sequentially on ROW_WID
df = dim_union.merge(source2, on='ROW_WID', how='inner')
df = df.merge(source3, on='ROW_WID', how='inner')
df = df.merge(source4, on='ROW_WID', how='inner')
df = df.merge(source5, on='ROW_WID', how='inner')
df = df.merge(source6, on='ROW_WID', how='inner')
df = df.merge(source7, on='ROW_WID', how='inner')

# Select only TECHSUPPORT_NUM column
result = df[['TECHSUPPORT_NUM']]

# Drop duplicates if any
result = result.drop_duplicates().reset_index(drop=True)

# Write output
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv', index=False)