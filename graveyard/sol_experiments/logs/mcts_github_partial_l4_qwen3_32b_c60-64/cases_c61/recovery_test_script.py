import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/test_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/test_2.csv', index_col=0)
df3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_61/test_3.csv', index_col=0)

combined = pd.concat([df0, df1, df2, df3], ignore_index=True)
result = combined.groupby('Población resto', as_index=False).first()
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts_recovery_test_val.csv')