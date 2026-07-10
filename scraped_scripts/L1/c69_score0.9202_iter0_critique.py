import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_69/training_1.csv", index_col=0)

# Join on city to combine city-level info with ride-level info
joined = pd.merge(df1, df0, how='inner', on='city')

# Reorder columns to match target schema
result = joined[['city', 'driver_count', 'type', 'date', 'fare', 'ride_id']]

# Ensure correct dtypes as per target schema
result['city'] = result['city'].astype(str)
result['driver_count'] = result['driver_count'].astype(int)
result['type'] = result['type'].astype(str)
result['date'] = result['date'].astype(str)
result['fare'] = result['fare'].astype(float)
result['ride_id'] = result['ride_id'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_69/target_multisource_mcts.csv", index=False)