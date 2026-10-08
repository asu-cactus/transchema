import pandas as pd

source_paths = [
    'autopipeline-benchmarks/github-pipelines/length9_97/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length9_97/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length9_97/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length9_97/test_3.csv',
    'autopipeline-benchmarks/github-pipelines/length9_97/test_4.csv',
    'autopipeline-benchmarks/github-pipelines/length9_97/test_5.csv',
    'autopipeline-benchmarks/github-pipelines/length9_97/test_6.csv',
    'autopipeline-benchmarks/github-pipelines/length9_97/test_7.csv',
    'autopipeline-benchmarks/github-pipelines/length9_97/test_8.csv',
    'autopipeline-benchmarks/github-pipelines/length9_97/test_9.csv'
]

dfs = [pd.read_csv(path, index_col=0) for path in source_paths]
combined = pd.concat(dfs, ignore_index=True)
combined.to_csv('autopipeline-benchmarks/github-pipelines/length9_97/target_multisource_mcts_recovery_test_val.csv')