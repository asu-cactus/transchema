import pandas as pd

dfs = []
for i in range(39):
    path = f'autopipeline-benchmarks/github-pipelines/length9_76/training_{i}.csv'
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

combined = pd.concat(dfs)
result = combined.groupby('genre')['members'].sum().reset_index()
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_76/target_multisource_mcts_recovery_test_val.csv', index=False)