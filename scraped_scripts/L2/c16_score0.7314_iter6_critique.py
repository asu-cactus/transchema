import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_16/training_1.csv", index_col=0)

# Join on city
merged = pd.merge(df1, df0[['city', 'driver_count']], on='city', how='inner')

# Group by city and aggregate
result = merged.groupby('city').agg(
    fare=('fare', 'mean'),
    ride_id=('ride_id', 'mean'),
    driver_count=('driver_count', 'sum')
).reset_index()

# Ensure correct types
result['fare'] = result['fare'].astype(float)
result['ride_id'] = result['ride_id'].astype(float)
result['driver_count'] = result['driver_count'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_16/target_multisource_mcts.csv", index=False)