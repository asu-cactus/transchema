import pandas as pd

# Load all source files with consistent schema
dfs = []
for i in range(10):
    file_path = f"autopipeline-benchmarks/github-pipelines/length9_84/training_{i}.csv"
    df = pd.read_csv(file_path, index_col=0)
    dfs.append(df)

# Combine all sources via concatenation
result = pd.concat(dfs, ignore_index=True)

# Save to target file
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_84/target_multisource_mcts_recovery_test_val.csv", index=False)