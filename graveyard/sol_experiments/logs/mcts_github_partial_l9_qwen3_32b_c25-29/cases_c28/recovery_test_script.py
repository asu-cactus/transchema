import pandas as pd

files = [
    'autopipeline-benchmarks/github-pipelines/length9_28/test_3.csv',
    'autopipeline-benchmarks/github-pipelines/length9_28/test_5.csv',
    'autopipeline-benchmarks/github-pipelines/length9_28/test_6.csv',
    'autopipeline-benchmarks/github-pipelines/length9_28/test_7.csv'
]

dfs = []
for file in files:
    df = pd.read_csv(file, index_col=0)
    dfs.append(df[['ARPU']])

result = pd.concat(dfs, ignore_index=True).astype({'ARPU': float})
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_28/target_multisource_mcts_recovery_test_val.csv')