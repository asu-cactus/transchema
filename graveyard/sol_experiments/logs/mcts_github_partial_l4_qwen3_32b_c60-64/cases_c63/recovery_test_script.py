import pandas as pd

# Read the three source CSV files with index_col=0 to ignore the first column as index
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_63/test_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_63/test_2.csv', index_col=0)
df3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_63/test_3.csv', index_col=0)

# Combine the DataFrames using pd.concat
combined_df = pd.concat([df1, df2, df3])

# Remove duplicate rows to match the target's unique structure
combined_df.drop_duplicates(inplace=True)

# Write the result to the target file
combined_df.to_csv('autopipeline-benchmarks/github-pipelines/length4_63/target_multisource_mcts_recovery_test_val.csv', index=False)