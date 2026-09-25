import pandas as pd

sources = [
    'autopipeline-benchmarks/github-pipelines/length9_3/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length9_3/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length9_3/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length9_3/test_3.csv',
    'autopipeline-benchmarks/github-pipelines/length9_3/test_4.csv',
    'autopipeline-benchmarks/github-pipelines/length9_3/test_5.csv',
    'autopipeline-benchmarks/github-pipelines/length9_3/test_6.csv',
    'autopipeline-benchmarks/github-pipelines/length9_3/test_7.csv',
    'autopipeline-benchmarks/github-pipelines/length9_3/test_8.csv',
    'autopipeline-benchmarks/github-pipelines/length9_3/test_9.csv',
    'autopipeline-benchmarks/github-pipelines/length9_3/test_10.csv'
]

dfs = [pd.read_csv(fn, index_col=0) for fn in sources]
unioned = pd.concat(dfs, ignore_index=True)

grouped = unioned.groupby('company_permalink').agg({
    'funded_year': 'max',
    'raised_amount_usd': 'sum'
}).reset_index()

grouped.to_csv('autopipeline-benchmarks/github-pipelines/length9_3/target_multisource_mcts_recovery_test_val.csv', index=False)