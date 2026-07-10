import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_73/training_1.csv", index_col=0)

grouped = df0.groupby('city', as_index=False).agg({'fare':'mean', 'ride_id':'mean'})

merged = pd.merge(df1, grouped, on='city', how='inner')

merged['fare'] = merged['fare'].astype(float)
merged['ride_id'] = merged['ride_id'].astype(float)
merged['driver_count'] = merged['driver_count'].astype(int)
merged['type'] = merged['type'].astype(str)
merged['city'] = merged['city'].astype(str)

result = merged[['type', 'city', 'fare', 'ride_id', 'driver_count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_73/target_multisource_mcts.csv", index=False)