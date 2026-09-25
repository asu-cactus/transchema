import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_1.csv", index_col=0)

# Aggregate Source1 by city: mean fare, count ride_id
agg_source1 = df1.groupby('city', as_index=False).agg({
    'fare': 'mean',
    'ride_id': 'count'
})

# Join aggregated Source1 with Source0 on city to get driver_count
merged = pd.merge(agg_source1, df0[['city', 'driver_count']], on='city', how='inner')

# Ensure correct types and column order
result = merged[['city', 'fare', 'ride_id', 'driver_count']]

result['fare'] = result['fare'].astype(float)
result['ride_id'] = result['ride_id'].astype(float)  # count is int but target schema is float
result['driver_count'] = result['driver_count'].astype(int)
result['city'] = result['city'].astype(str)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length2_11/target_multisource_mcts.csv", index=False)