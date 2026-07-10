import pandas as pd

# Read dimension tables and union them
dim3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv', index_col=0)
dim4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv', index_col=0)
dim7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv', index_col=0)
dim8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv', index_col=0)

unioned_dim = pd.concat([dim3, dim4, dim7, dim8], ignore_index=True)

# Read aspect tables
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv', index_col=0)
source5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv', index_col=0)
source6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv', index_col=0)
source9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv', index_col=0)

# Join unioned_dim with all aspect tables on ROW_WID
df = unioned_dim.merge(source0, on='ROW_WID', how='inner')
df = df.merge(source1, on='ROW_WID', how='inner')
df = df.merge(source2, on='ROW_WID', how='inner')
df = df.merge(source5, on='ROW_WID', how='inner')
df = df.merge(source6, on='ROW_WID', how='inner')
df = df.merge(source9, on='ROW_WID', how='inner')

# Project only INBOUND_CALLS_NUM as per target schema
result = df[['INBOUND_CALLS_NUM']]

# Write output
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv', index=False)