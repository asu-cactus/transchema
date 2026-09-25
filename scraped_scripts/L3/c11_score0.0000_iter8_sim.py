import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_11/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_11/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_11/training_2.csv', index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

result = df[['SN', 'Price']].copy()
result['count'] = 1
result['SN'] = result['SN'].astype(str)
result['Price'] = result['Price'].astype(float)
result['count'] = result['count'].astype(int)

result.to_csv('autopipeline-benchmarks/github-pipelines/length3_11/target_multisource_mcts.csv', index=False)