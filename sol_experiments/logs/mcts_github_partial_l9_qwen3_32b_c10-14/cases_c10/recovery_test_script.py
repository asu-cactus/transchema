import pandas as pd

# Load all source CSV files with index_col=0 to ignore the first column (auto-detected index)
df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_10/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_10/test_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_10/test_2.csv', index_col=0)
df3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_10/test_3.csv', index_col=0)
df4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_10/test_4.csv', index_col=0)
df5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_10/test_5.csv', index_col=0)
df6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_10/test_6.csv', index_col=0)
df7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_10/test_7.csv', index_col=0)
df8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_10/test_8.csv', index_col=0)
df9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_10/test_9.csv', index_col=0)

# Combine all dataframes using pd.concat with ignore_index to reset indices
combined_df = pd.concat([df0, df1, df2, df3, df4, df5, df6, df7, df8, df9], ignore_index=True)

# Save the result to the target CSV file without index
combined_df.to_csv('autopipeline-benchmarks/github-pipelines/length9_10/target_multisource_mcts_recovery_test_val.csv', index=False)