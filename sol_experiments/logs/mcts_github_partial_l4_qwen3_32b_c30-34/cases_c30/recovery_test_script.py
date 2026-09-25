import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_30/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_30/test_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_30/test_2.csv', index_col=0)
df3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_30/test_3.csv', index_col=0)
df4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_30/test_4.csv', index_col=0)

result = pd.concat([df0,df1,df2,df3,df4], ignore_index=True)
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_30/target_multisource_mcts_recovery_test_val.csv')