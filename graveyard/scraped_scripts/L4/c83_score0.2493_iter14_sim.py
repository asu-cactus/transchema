import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

source0_subset = source0[['city', 'fare']]
source0_subset['type'] = pd.NA
source0_subset['driver_count'] = pd.NA

source1_subset = source1[['city', 'driver_count', 'type']]
source1_subset['fare'] = pd.NA

union_result = pd.concat([source0_subset, source1_subset], ignore_index=True, sort=False)

joined = union_result.merge(source0[['city', 'fare']], on='city', how='left', suffixes=('', '_source0'))

joined['average_fare'] = joined['fare'].combine_first(joined['fare_source0']).astype(float)
joined['driver_count'] = joined['driver_count'].astype('Int64')
joined['type'] = joined['type'].astype('string')
joined['city'] = joined['city'].astype('string')

result = joined[['city', 'driver_count', 'type', 'average_fare']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)