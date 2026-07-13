import pandas as pd

dfs = []
for i in range(10):
    path = f'autopipeline-benchmarks/github-pipelines/length9_87/training_{i}.csv'
    dfs.append(pd.read_csv(path, index_col=0))

final_df = pd.concat(dfs, ignore_index=True)
final_df.to_csv('autopipeline-benchmarks/github-pipelines/length9_87/target_multisource_mcts_recovery_test_val.csv')