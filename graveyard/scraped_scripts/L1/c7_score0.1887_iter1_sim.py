import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/training_1.csv", index_col=0)

df0['date'] = pd.NA
df0['fare'] = pd.NA
df0['ride_id'] = pd.NA

df1['driver_count'] = pd.NA
df1['type'] = pd.NA

union_result = pd.concat([df0, df1], ignore_index=True, sort=False)

merged = pd.merge(union_result, df1, on='city', how='left', suffixes=('', '_y'))

merged['driver_count'] = merged['driver_count'].combine_first(merged['driver_count_y'])
merged['type'] = merged['type'].combine_first(merged['type_y'])
merged['date'] = merged['date'].combine_first(merged['date'])
merged['fare'] = merged['fare'].combine_first(merged['fare'])
merged['ride_id'] = merged['ride_id'].combine_first(merged['ride_id'])

result = merged[['city', 'driver_count', 'type', 'date', 'fare', 'ride_id']]

result['driver_count'] = pd.to_numeric(result['driver_count'], errors='coerce').astype('Int64')
result['type'] = result['type'].astype('string')
result['date'] = result['date'].astype('string')
result['fare'] = pd.to_numeric(result['fare'], errors='coerce')
result['ride_id'] = pd.to_numeric(result['ride_id'], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_7/target_multisource_mcts.csv", index=False)