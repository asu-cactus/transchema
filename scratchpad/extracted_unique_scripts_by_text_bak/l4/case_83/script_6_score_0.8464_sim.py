import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

df0_agg = df0.groupby('city').agg(average_fare=('fare', 'mean'), ride_count=('ride_id', 'count')).reset_index()
df0_agg['type'] = 'Urban'  # placeholder, will be replaced by pivot

df1_renamed = df1.rename(columns={'driver_count': 'driver_count', 'type': 'type', 'city': 'city'})

merged = pd.merge(df1_renamed, df0_agg[['city', 'average_fare']], on='city', how='left')

result = merged[['city', 'driver_count', 'type', 'average_fare']]

result['driver_count'] = result['driver_count'].astype('Int64')
result['average_fare'] = result['average_fare'].astype(float)
result['city'] = result['city'].astype(str)
result['type'] = result['type'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)