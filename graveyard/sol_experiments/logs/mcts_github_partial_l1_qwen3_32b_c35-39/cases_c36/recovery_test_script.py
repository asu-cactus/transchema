import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_36/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_36/test_1.csv', index_col=0)

combined = pd.concat([df0, df1], ignore_index=True)
combined.to_csv('autopipeline-benchmarks/github-pipelines/length1_36/target_multisource_mcts_recovery_test_val.csv')