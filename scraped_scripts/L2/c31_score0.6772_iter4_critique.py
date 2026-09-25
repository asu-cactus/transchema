import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_1.csv", index_col=0)

# Join on city to get type from df0 associated with rides in df1
df_joined = df0[['type', 'city', 'driver_count']].merge(df1[['city', 'fare', 'ride_id']], on='city', how='inner')

# Group by type and city, aggregate fare (mean), ride_id (count), driver_count (sum)
result = df_joined.groupby(['type', 'city'], as_index=False).agg({
    'fare': 'mean',
    'ride_id': 'count',
    'driver_count': 'sum'
})

# Rename columns to match target schema exactly
result = result.rename(columns={
    'fare': 'fare',
    'ride_id': 'ride_id',
    'driver_count': 'driver_count',
    'type': 'type',
    'city': 'city'
})

# Cast columns to correct types
result['fare'] = result['fare'].astype(float)
result['ride_id'] = result['ride_id'].astype(float)  # target ride_id is float
result['driver_count'] = result['driver_count'].astype(int)
result['type'] = result['type'].astype(str)
result['city'] = result['city'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_31/target_multisource_mcts.csv", index=False)