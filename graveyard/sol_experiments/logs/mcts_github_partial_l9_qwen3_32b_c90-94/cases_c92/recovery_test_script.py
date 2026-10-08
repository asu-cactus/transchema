import pandas as pd

dfs = []
for i in range(10):
    path = f'autopipeline-benchmarks/github-pipelines/length9_92/training_{i}.csv'
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)
combined.to_csv('autopipeline-benchmarks/github-pipelines/length9_92/target_multisource_mcts_recovery_test_val.csv', index=False)