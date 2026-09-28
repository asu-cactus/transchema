import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_1.csv", index_col=0)

agg1 = df1.groupby('city').agg(fare=('fare', 'max'), ride_id=('ride_id', 'count')).reset_index()
agg0 = df0.groupby(['city', 'type']).agg(driver_count=('driver_count', 'sum')).reset_index()

joined = pd.merge(df0, agg1, how='inner', on='city')
joined = pd.merge(joined, agg0, how='inner', on=['city', 'type'], suffixes=('', '_agg0'))

grouped = joined.groupby('city').agg(
    driver_count=('driver_count_agg0', 'sum'),
    fare=('fare', 'max'),
    ride_id=('ride_id', 'sum')
).reset_index()

grouped['driver_count'] = grouped['driver_count'].astype(int)
grouped['fare'] = grouped['fare'].astype(float)
grouped['ride_id'] = grouped['ride_id'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_63/target_multisource_mcts.csv", index=False)