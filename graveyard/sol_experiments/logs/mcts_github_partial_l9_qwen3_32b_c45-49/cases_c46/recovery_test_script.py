import pandas as pd
import os

base_path = 'autopipeline-benchmarks/github-pipelines/length9_46/'
sources = [f'training_{i}.csv' for i in range(15)]

dfs = []
for file in sources:
    df = pd.read_csv(os.path.join(base_path, file), index_col=0)
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)
combined.to_csv('autopipeline-benchmarks/github-pipelines/length9_46/target_multisource_mcts_recovery_test_val.csv', index=False)