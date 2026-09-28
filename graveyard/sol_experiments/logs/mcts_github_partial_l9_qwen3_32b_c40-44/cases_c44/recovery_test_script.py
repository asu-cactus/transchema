import pandas as pd

# Read all source CSV files with index_col=0
dfs = []
for i in range(222):  # From Source9_44_0 to Source9_44_221
    file_path = f'autopipeline-benchmarks/github-pipelines/length9_44/training_{i}.csv'
    df = pd.read_csv(file_path, index_col=0)
    dfs.append(df)

# Perform UNION on all source dataframes
union_df = pd.concat(dfs, ignore_index=True)

# Save the result to the target file
union_df.to_csv('autopipeline-benchmarks/github-pipelines/length9_44/target_multisource_mcts_recovery_test_val.csv', index=False)