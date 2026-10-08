import pandas as pd

dfs = []
for i in range(11):
    path = f'autopipeline-benchmarks/github-pipelines/length9_0/training_{i}.csv'
    df = pd.read_csv(path, index_col=0)
    df['0'] = df['0'].astype(int)
    dfs.append(df)

result = pd.concat(dfs, ignore_index=True)
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_0/target_multisource_mcts_recovery_test_val.csv')