import pandas as pd

dfs = []
for path in [
    'autopipeline-benchmarks/github-pipelines/length4_41/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length4_41/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length4_41/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length4_41/test_3.csv'
]:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)
combined['x'] = combined['x'].astype(int)
combined['label'] = combined['label'].replace({'g': 0, 'r': 1, 'purple': 2, 'b': 3})
combined.to_csv('autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts_recovery_test_val.csv')