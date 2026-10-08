import pandas as pd

# Load source tables
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/test_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/test_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/test_3.csv', index_col=0)
source4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/test_4.csv', index_col=0)
source5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/test_5.csv', index_col=0)
source6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/test_6.csv', index_col=0)
source7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/test_7.csv', index_col=0)
source8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/test_8.csv', index_col=0)
source9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_34/test_9.csv', index_col=0)

# Union sources with the same schema
source2568 = pd.concat([source2, source5, source6, source8], ignore_index=True)

# Inner joins to ensure common ROW_WID
joined_df = source2568.merge(source9, on='ROW_WID', how='inner')
joined_df = joined_df.merge(source0, on='ROW_WID', how='inner')
joined_df = joined_df.merge(source1, on='ROW_WID', how='inner')
joined_df = joined_df.merge(source3, on='ROW_WID', how='inner')
joined_df = joined_df.merge(source4, on='ROW_WID', how='inner')
joined_df = joined_df.merge(source7, on='ROW_WID', how='inner')

# Select only the target column
result = joined_df[['KEYWORDS_NUM']]

# Write result to file
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts_recovery_test_val.csv', index=False)