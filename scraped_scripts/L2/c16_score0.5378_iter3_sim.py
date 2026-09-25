import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_16/training_1.csv", index_col=0)

merged = pd.merge(df1, df0[['city', 'driver_count']], on='city')

merged = merged[['city', 'fare', 'ride_id', 'driver_count']]

merged['fare'] = merged['fare'].astype(float)
merged['ride_id'] = merged['ride_id'].astype(float)
merged['driver_count'] = merged['driver_count'].astype(int)
merged['city'] = merged['city'].astype(str)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_16/target_multisource_mcts.csv", index=False)