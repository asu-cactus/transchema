import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_63/training_1.csv", index_col=0)

# Join on city
joined = pd.merge(df0, df1, how='inner', on='city')

# Group by city and aggregate
result = joined.groupby('city').agg(
    driver_count=('driver_count', 'sum'),
    fare=('fare', 'mean'),
    ride_id=('ride_id', 'count')
).reset_index()

# Cast types to match target schema
result['driver_count'] = result['driver_count'].astype(int)
result['fare'] = result['fare'].astype(float)
result['ride_id'] = result['ride_id'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_63/target_multisource_mcts.csv", index=False)