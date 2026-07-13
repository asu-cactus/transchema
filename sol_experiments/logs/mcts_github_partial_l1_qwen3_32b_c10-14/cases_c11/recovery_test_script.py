import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_11/test_0.csv', index_col=0)
result = df.groupby('sex')[['births']].sum().reset_index()
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_11/target_multisource_mcts_recovery_test_val.csv', index=False)