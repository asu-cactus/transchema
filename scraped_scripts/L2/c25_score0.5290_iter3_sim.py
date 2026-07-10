import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_1.csv", index_col=0)

pivot_result = df0.pivot_table(index='city', columns='type', values='driver_count', aggfunc='sum').reset_index()
pivot_result.columns.name = None
pivot_result = pivot_result.rename(columns={'Urban': 'driver_count'})

merged = pd.merge(pivot_result[['city', 'driver_count']], df1[['city', 'fare', 'ride_id']], on='city')

merged['driver_count'] = merged['driver_count'].fillna(0).astype(int)
merged['fare'] = merged['fare'].astype(float)
merged['ride_id'] = merged['ride_id'].astype(float)
merged['city'] = merged['city'].astype(str)

merged = merged[['city', 'fare', 'ride_id', 'driver_count']]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_25/target_multisource_mcts.csv", index=False)