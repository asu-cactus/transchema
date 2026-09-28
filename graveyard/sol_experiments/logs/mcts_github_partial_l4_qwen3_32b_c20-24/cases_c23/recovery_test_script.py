import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_23/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_23/test_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_23/test_2.csv', index_col=0)
df3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_23/test_3.csv', index_col=0)
df4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_23/test_4.csv', index_col=0)

joined = pd.merge(df2, df3, on='placeID', how='inner')
joined = pd.merge(joined, df0, on='placeID', how='inner')
joined = pd.merge(joined, df1, on='placeID', how='inner')
joined = pd.merge(joined, df4, on='placeID', how='inner')

joined.drop(columns=['Rpayment'], inplace=True)
joined.to_csv('autopipeline-benchmarks/github-pipelines/length4_23/target_multisource_mcts_recovery_test_val.csv')