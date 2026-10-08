import pandas as pd

# Load all source files with proper index handling
df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_2.csv', index_col=0)
df3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_3.csv', index_col=0)
df4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_4.csv', index_col=0)
df5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_5.csv', index_col=0)
df6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_6.csv', index_col=0)
df7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_7.csv', index_col=0)
df8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_8.csv', index_col=0)
df9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_9.csv', index_col=0)
df10 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_10.csv', index_col=0)
df11 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_11.csv', index_col=0)
df12 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_12.csv', index_col=0)
df13 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_13.csv', index_col=0)
df14 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_53/test_14.csv', index_col=0)

# Combine all dataframes through union operation
combined_df = pd.concat([df0, df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12, df13, df14], ignore_index=True)

# Ensure correct data types
combined_df['addr_state'] = combined_df['addr_state'].astype(int)

# Remove duplicate rows if any
combined_df = combined_df.drop_duplicates()

# Save to target file
combined_df.to_csv('autopipeline-benchmarks/github-pipelines/length9_53/target_multisource_mcts_recovery_test_val.csv', index=False)