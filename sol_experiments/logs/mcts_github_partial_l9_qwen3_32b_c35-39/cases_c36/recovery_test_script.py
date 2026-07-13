import pandas as pd
from functools import reduce

# Read all source files
sources = []
for i in range(135):  # 0-134 inclusive
    file_path = f'autopipeline-benchmarks/github-pipelines/length9_36/training_{i}.csv'
    df = pd.read_csv(file_path, index_col=0)
    sources.append(df)

# Perform UNION operation by concatenating all DataFrames
union_df = pd.concat(sources)

# Perform GROUP BY and SUM operation
aggregated_df = union_df.groupby(["name", "sex"], as_index=False)["number"].sum()

# Save to target file
aggregated_df.to_csv('autopipeline-benchmarks/github-pipelines/length9_36/target_multisource_mcts_recovery_test_val.csv', index=False)