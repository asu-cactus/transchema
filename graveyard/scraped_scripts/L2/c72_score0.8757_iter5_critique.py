import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_72/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_72/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_72/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on city
merged = pd.merge(df0, df1, on='city', how='inner')

# Aggregate over entire joined data (no group by)
result = pd.DataFrame({
    'type': [merged['type'].iloc[0]],  # take first type value
    'fare': [merged['fare'].sum()],
    'ride_id': [merged['ride_id'].count()],
    'driver_count': [merged['driver_count'].sum()]
})

# Ensure correct dtypes
result['type'] = result['type'].astype(str)
result['fare'] = result['fare'].astype(float)
result['ride_id'] = result['ride_id'].astype(int)
result['driver_count'] = result['driver_count'].astype(int)

result.to_csv(target_path, index=False)