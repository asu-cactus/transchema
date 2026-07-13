import pandas as pd

dfs = [
    pd.read_csv(f'autopipeline-benchmarks/github-pipelines/length9_54/training_{i}.csv', index_col=0)
    for i in range(15)
]

combined = pd.concat(dfs, ignore_index=True)
combined.to_csv('autopipeline-benchmarks/github-pipelines/length9_54/target_multisource_mcts_recovery_test_val.csv')