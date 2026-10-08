import pandas as pd

dfs = []
for i in [0,1,2,3,4,5,6,7,8,9]:
    df = pd.read_csv(f'autopipeline-benchmarks/github-pipelines/length9_90/training_{i}.csv', index_col=0)
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)
combined = combined.astype({'admit': 'int64', 'gre': 'int64', 'gpa': 'float64', 'prestige': 'int64'})
combined.to_csv('autopipeline-benchmarks/github-pipelines/length9_90/target_multisource_mcts_recovery_test_val.csv', index=False)