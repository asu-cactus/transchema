import pandas as pd

sources = [
    'autopipeline-benchmarks/github-pipelines/length9_26/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length9_26/test_3.csv',
    'autopipeline-benchmarks/github-pipelines/length9_26/test_4.csv',
    'autopipeline-benchmarks/github-pipelines/length9_26/test_8.csv'
]

dfs = []
for path in sources:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df[['CANCEL_DT']])

combined = pd.concat(dfs, ignore_index=True)
result = combined.drop_duplicates().reset_index(drop=True)
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_26/target_multisource_mcts_recovery_test_val.csv', index=False)