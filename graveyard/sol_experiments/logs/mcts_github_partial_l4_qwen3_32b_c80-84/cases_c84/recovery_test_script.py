import pandas as pd

dfs = [
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_84/test_0.csv', index_col=0),
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_84/test_1.csv', index_col=0),
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_84/test_2.csv', index_col=0),
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_84/test_3.csv', index_col=0),
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_84/test_4.csv', index_col=0)
]

result = pd.concat(dfs, ignore_index=True)
result = result[result['Count'].notna()]
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_84/target_multisource_mcts_recovery_test_val.csv', index=False)