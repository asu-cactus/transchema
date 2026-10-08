import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_9/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_9/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=['city', 'date'], value_vars=['fare', 'ride_id'], var_name='attribute', value_name='value')

df_joined = pd.merge(df0_unpivot, df1, on='city', how='inner')

result = df_joined.groupby('city', as_index=False)['driver_count'].sum()
result['driver_count'] = result['driver_count'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_9/target_multisource_mcts.csv", index=False)