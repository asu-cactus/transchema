import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

# Join on city (inner join to keep only cities present in both)
merged = pd.merge(df1, df0, on='city', how='inner')

# Group by city, driver_count, type and aggregate average fare
result = merged.groupby(['city', 'driver_count', 'type'], as_index=False).agg(average_fare=('fare', 'mean'))

# Ensure correct dtypes as per target schema
result['city'] = result['city'].astype(str)
result['driver_count'] = result['driver_count'].astype('Int64')
result['type'] = result['type'].astype(str)
result['average_fare'] = result['average_fare'].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)