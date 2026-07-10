import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_1.csv", index_col=0)

agg_df1 = df1.groupby('city').agg(
    fare_min=('fare', 'min'),
    ride_id_nunique=('ride_id', 'nunique')
).reset_index()

agg_df0 = df0.groupby(['city', 'type']).agg(
    driver_count_avg=('driver_count', 'mean')
).reset_index()

merged = pd.merge(agg_df0, agg_df1, on='city', how='inner')

result = merged.rename(columns={
    'city': 'city',
    'driver_count_avg': 'driver_count',
    'fare_min': 'fare',
    'ride_id_nunique': 'ride_id'
})[['city', 'driver_count', 'fare', 'ride_id']]

result['driver_count'] = result['driver_count'].round().astype('Int64')
result['fare'] = result['fare'].astype(float)
result['ride_id'] = result['ride_id'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_63/target_multisource_mcts.csv", index=False)