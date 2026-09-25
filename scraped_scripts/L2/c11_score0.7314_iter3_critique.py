import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_1.csv", index_col=0)

# Join on city
merged = pd.merge(df0, df1, on='city', how='inner')

# Group by city and aggregate
result = merged.groupby('city', as_index=False).agg({
    'fare': 'mean',
    'ride_id': 'mean',
    'driver_count': 'sum'
})

# Ensure correct dtypes
result['city'] = result['city'].astype(str)
result['fare'] = result['fare'].astype(float)
result['ride_id'] = result['ride_id'].astype(float)
result['driver_count'] = result['driver_count'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_11/target_multisource_mcts.csv", index=False)