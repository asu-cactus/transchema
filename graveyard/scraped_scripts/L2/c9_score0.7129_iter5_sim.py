import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_9/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_9/training_1.csv", index_col=0)

# From Source0: count distinct ride_id per city as driver_count
driver_count_0 = df0.groupby('city', as_index=False).agg(driver_count=('ride_id', 'count'))

# From Source1: select city and driver_count directly
driver_count_1 = df1[['city', 'driver_count']]

# Combine both sources by city and sum driver_count
combined = pd.concat([driver_count_0, driver_count_1], ignore_index=True)
result = combined.groupby('city', as_index=False).agg(driver_count=('driver_count', 'sum'))

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_9/target_multisource_mcts.csv", index=False)