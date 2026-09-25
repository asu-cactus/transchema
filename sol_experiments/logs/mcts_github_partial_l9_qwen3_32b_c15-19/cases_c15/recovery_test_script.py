import pandas as pd

dfs = [
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_15/test_0.csv', index_col=0),
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_15/test_1.csv', index_col=0),
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_15/test_2.csv', index_col=0),
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_15/test_3.csv', index_col=0),
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_15/test_4.csv', index_col=0),
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_15/test_5.csv', index_col=0)
]

combined = pd.concat(dfs, ignore_index=True)
target_columns = [
    'State Name', 'Year', 'Month', 'county Name', 'State Code', 'County Code', 
    'Date', 'AQI', 'Category', 'Defining Parameter', 'Defining Site', 
    'Number of Sites Reporting'
]
combined = combined[target_columns]
combined.to_csv('autopipeline-benchmarks/github-pipelines/length9_15/target_multisource_mcts_recovery_test_val.csv', index=False)