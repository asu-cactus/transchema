import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_38/test_0.csv', index_col=0)
df3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_38/test_3.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_38/test_2.csv', index_col=0)
df4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_38/test_4.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_38/test_1.csv', index_col=0)

df = df0.merge(df3, on='placeID', how='left')
df = df.merge(df2, on='placeID', how='left')
df = df.merge(df4, on='placeID', how='left')
df = df.merge(df1, on='placeID', how='left')

df.to_csv('autopipeline-benchmarks/github-pipelines/length4_38/target_multisource_mcts_recovery_test_val.csv')