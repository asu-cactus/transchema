import pandas as pd

dfs = []
for i in range(10):
    df = pd.read_csv(f'autopipeline-benchmarks/github-pipelines/length9_66/training_{i}.csv', index_col=0)
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)
combined.to_csv('autopipeline-benchmarks/github-pipelines/length9_66/target_multisource_mcts_recovery_test_val.csv')