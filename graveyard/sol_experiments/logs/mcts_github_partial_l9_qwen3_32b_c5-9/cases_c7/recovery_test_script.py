import pandas as pd

# Load all source tables with index_col=0
source_paths = [
    'autopipeline-benchmarks/github-pipelines/length9_7/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length9_7/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length9_7/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length9_7/test_3.csv',
    'autopipeline-benchmarks/github-pipelines/length9_7/test_4.csv',
    'autopipeline-benchmarks/github-pipelines/length9_7/test_5.csv',
    'autopipeline-benchmarks/github-pipelines/length9_7/test_6.csv',
    'autopipeline-benchmarks/github-pipelines/length9_7/test_7.csv',
    'autopipeline-benchmarks/github-pipelines/length9_7/test_8.csv',
    'autopipeline-benchmarks/github-pipelines/length9_7/test_9.csv'
]

dfs = [pd.read_csv(p, index_col=0) for p in source_paths]

# Perform union
target_df = pd.concat(dfs, ignore_index=True)

# Save result to target file
target_df.to_csv('autopipeline-benchmarks/github-pipelines/length9_7/target_multisource_mcts_recovery_test_val.csv')