import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

# Join source0 and source1 on city (inner join)
merged = pd.merge(source0, source1, on='city', how='inner')

# Group by city, driver_count, type and aggregate average fare
result = merged.groupby(['city', 'driver_count', 'type'], as_index=False)['fare'].mean()

# Rename fare to average_fare to match target schema
result = result.rename(columns={'fare': 'average_fare'})

# Ensure correct dtypes
result['city'] = result['city'].astype(str)
result['driver_count'] = result['driver_count'].astype(int)
result['type'] = result['type'].astype(str)
result['average_fare'] = result['average_fare'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)