import pandas as pd
import glob

# Read all source CSV files in order
sources = []
for i in range(222):  # 0 to 221 inclusive
    file_path = f'autopipeline-benchmarks/github-pipelines/length9_41/training_{i}.csv'
    df = pd.read_csv(file_path, index_col=0)
    sources.append(df)

# Union all source tables
result = pd.concat(sources, ignore_index=True)

# Save to target file
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_41/target_multisource_mcts_recovery_test_val.csv', index=False)