import pandas as pd

dfs = []
for i in range(39):  # 0 to 38 covers all source files listed
    path = f'autopipeline-benchmarks/github-pipelines/length9_77/training_{i}.csv'
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

result = pd.concat(dfs, ignore_index=True)
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_77/target_multisource_mcts_recovery_test_val.csv')