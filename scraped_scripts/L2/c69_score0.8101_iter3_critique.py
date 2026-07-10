import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_69/training_1.csv", index_col=0)

# Count rides per city in df1
df1_counts = df1.groupby('city', as_index=False)['ride_id'].count()
df1_counts.rename(columns={'ride_id': 'ride_count'}, inplace=True)

# Join df0 and df1_counts on city
df_joined = pd.merge(df0[['city', 'driver_count']], df1_counts, on='city', how='inner')

# Sum driver_count and ride_count as driver_count in result
result = df_joined.copy()
result['driver_count'] = result['driver_count'] + result['ride_count']

# Keep only required columns
result = result[['city', 'driver_count']]

# Ensure driver_count is integer type
result['driver_count'] = result['driver_count'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_69/target_multisource_mcts.csv", index=False)