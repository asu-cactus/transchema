import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_73/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on='city', how='inner')

grouped = merged.groupby(['type', 'city'], as_index=False).agg({
    'fare': 'mean',
    'ride_id': 'mean',
    'driver_count': 'max'
})

grouped['fare'] = grouped['fare'].astype(float)
grouped['ride_id'] = grouped['ride_id'].astype(float)
grouped['driver_count'] = grouped['driver_count'].astype(int)
grouped['type'] = grouped['type'].astype(str)
grouped['city'] = grouped['city'].astype(str)

result = grouped[['type', 'city', 'fare', 'ride_id', 'driver_count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_73/target_multisource_mcts.csv", index=False)