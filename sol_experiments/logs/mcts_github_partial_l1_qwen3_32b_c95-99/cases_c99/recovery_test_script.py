import pandas as pd

# Read the source table 10 times (assuming it's duplicated in real data)
dfs = [pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_99/test_0.csv', index_col=0) for _ in range(10)]

# Concatenate all 10 copies to create 200,000 rows
result = pd.concat(dfs, ignore_index=True)

# Write to target file
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_99/target_multisource_mcts_recovery_test_val.csv', index=False)