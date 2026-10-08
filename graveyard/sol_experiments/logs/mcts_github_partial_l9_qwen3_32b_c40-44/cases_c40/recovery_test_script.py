import pandas as pd

files = [
    'autopipeline-benchmarks/github-pipelines/length9_40/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length9_40/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length9_40/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length9_40/test_3.csv',
    'autopipeline-benchmarks/github-pipelines/length9_40/test_4.csv',
    'autopipeline-benchmarks/github-pipelines/length9_40/test_5.csv',
    'autopipeline-benchmarks/github-pipelines/length9_40/test_6.csv',
    'autopipeline-benchmarks/github-pipelines/length9_40/test_7.csv',
    'autopipeline-benchmarks/github-pipelines/length9_40/test_8.csv',
    'autopipeline-benchmarks/github-pipelines/length9_40/test_9.csv',
    'autopipeline-benchmarks/github-pipelines/length9_40/test_10.csv'
]

dfs = []
for file in files:
    df = pd.read_csv(file, index_col=0)
    grouped = df.groupby('company_permalink').agg(
        {'raised_amount_usd': 'sum', 'funded_year': 'max'}
    ).reset_index()
    dfs.append(grouped)

result = pd.concat(dfs, ignore_index=True)
result.to_csv(
    'autopipeline-benchmarks/github-pipelines/length9_40/target_multisource_mcts_recovery_test_val.csv', 
    index=False
)