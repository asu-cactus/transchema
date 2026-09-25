import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

# Join source0 and source1 on city to get driver_count and type for each ride
joined = pd.merge(source0, source1, on='city', how='inner')

# Group by city, driver_count, and type, aggregate average fare
grouped = joined.groupby(['city', 'driver_count', 'type'], as_index=False).agg(average_fare=('fare', 'mean'))

# Ensure driver_count is integer type as in target schema
grouped['driver_count'] = grouped['driver_count'].astype(int)

# Reorder columns to match target schema: ['city', 'driver_count', 'type', 'average_fare']
grouped = grouped[['city', 'driver_count', 'type', 'average_fare']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)