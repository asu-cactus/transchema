import pandas as pd

dfs = []
for i in range(10):
    path = f'autopipeline-benchmarks/github-pipelines/length9_91/training_{i}.csv'
    dfs.append(pd.read_csv(path, index_col=0))

result = pd.concat(dfs, ignore_index=True)
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_91/target_multisource_mcts_recovery_test_val.csv')