import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_69/training_1.csv", index_col=0)

agg_df0 = df0.groupby(['type', 'city'], as_index=False).agg({'driver_count':'sum'})
agg_df1 = df1.groupby('city', as_index=False).agg({'fare':'mean', 'ride_id':'count'})

merged = pd.merge(agg_df0, agg_df1, how='inner', on='city')

merged = merged.rename(columns={
    'driver_count': 'driver_count',
    'type': 'type',
    'city': 'city',
    'fare': 'fare',
    'ride_id': 'ride_id'
})

merged['date'] = ''  # No date info from aggregation, fill with empty string

merged = merged[['city', 'driver_count', 'type', 'date', 'fare', 'ride_id']]

merged['driver_count'] = merged['driver_count'].astype(int)
merged['ride_id'] = merged['ride_id'].astype(int)
merged['fare'] = merged['fare'].astype(float)
merged['city'] = merged['city'].astype(str)
merged['type'] = merged['type'].astype(str)
merged['date'] = merged['date'].astype(str)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_69/target_multisource_mcts.csv", index=False)