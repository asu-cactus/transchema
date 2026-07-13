import pandas as pd

source_files = [
    'autopipeline-benchmarks/github-pipelines/length9_81/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length9_81/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length9_81/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length9_81/test_3.csv',
    'autopipeline-benchmarks/github-pipelines/length9_81/test_4.csv',
    'autopipeline-benchmarks/github-pipelines/length9_81/test_5.csv',
    'autopipeline-benchmarks/github-pipelines/length9_81/test_6.csv',
    'autopipeline-benchmarks/github-pipelines/length9_81/test_7.csv',
    'autopipeline-benchmarks/github-pipelines/length9_81/test_8.csv',
    'autopipeline-benchmarks/github-pipelines/length9_81/test_9.csv'
]

dfs = [pd.read_csv(f, index_col=0) for f in source_files]
combined = pd.concat(dfs, ignore_index=True)
combined.to_csv('autopipeline-benchmarks/github-pipelines/length9_81/target_multisource_mcts_recovery_test_val.csv')