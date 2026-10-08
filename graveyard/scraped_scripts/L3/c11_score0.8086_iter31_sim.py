import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_11/training_0.csv", index_col=0)

df_pivot = df0[['SN', 'Price']]

result = df_pivot.groupby('SN', as_index=False).agg({'Price':'first', 'SN':'count'})
result.rename(columns={'SN':'count'}, inplace=True)
result['Price'] = result['Price'].astype(float)
result['count'] = result['count'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_11/target_multisource_mcts.csv", index=False)