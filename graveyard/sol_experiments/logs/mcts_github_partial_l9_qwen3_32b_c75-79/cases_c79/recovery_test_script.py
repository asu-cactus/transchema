import pandas as pd

# Read all source files
sources = []
for i in range(57):
    file_path = f'autopipeline-benchmarks/github-pipelines/length9_79/training_{i}.csv'
    df = pd.read_csv(file_path)
    sources.append(df)

# Union all sources
target_table = pd.concat(sources, ignore_index=True)

# Write to target file
target_table.to_csv('autopipeline-benchmarks/github-pipelines/length9_79/target_multisource_mcts_recovery_test_val.csv', index=False)