import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_24/test_0.csv', index_col=0)
result = df0.groupby('condition')['click'].count().reset_index()
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_24/target_multisource_mcts_recovery_test_val.csv', index=False)