import pandas as pd

# Read all source tables
dfs = []
for i in range(15):
    filename = f"autopipeline-benchmarks/github-pipelines/length9_52/training_{i}.csv"
    df = pd.read_csv(filename, index_col=0)
    dfs.append(df)

# Union all source tables
combined = pd.concat(dfs, ignore_index=True)

# Export final result without grouping
combined.to_csv("autopipeline-benchmarks/github-pipelines/length9_52/target_multisource_mcts_recovery_test_val.csv", index=False)