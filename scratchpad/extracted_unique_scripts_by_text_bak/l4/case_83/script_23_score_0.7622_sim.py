import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

agg = source0.groupby('city').agg(driver_count=('ride_id', 'count'), average_fare=('fare', 'mean')).reset_index()

# The partial plan groups by city and type from Source1, so we need to join Source1 with the aggregation on city and type.
# But source0 has no 'type' column, so we must join source0 and source1 first on city to get 'type' for each ride, then aggregate by city and type.

# Join source0 and source1 on city to get 'type' for each ride
joined = pd.merge(source0, source1, on='city', how='inner')

# Now group by city and type, aggregate count of ride_id and average fare
grouped = joined.groupby(['city', 'type']).agg(driver_count=('ride_id', 'count'), average_fare=('fare', 'mean')).reset_index()

# The target schema is ['city': string, 'driver_count': integer, 'type': string, 'average_fare': float]
# Ensure driver_count is integer
grouped['driver_count'] = grouped['driver_count'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)