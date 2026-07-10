import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_1.csv", index_col=0)

pivot_result = df0.pivot(index='right_index', columns='type', values='driver_count').reset_index()
pivot_result = df0[['right_index', 'city', 'type', 'driver_count']]
pivot_result = pivot_result.pivot(index=['right_index', 'city'], columns='type', values='driver_count').reset_index()
pivot_result = pivot_result.rename_axis(None, axis=1)

# The pivot creates columns for each 'type' with driver_count values.
# But target schema expects 'type', 'city', 'driver_count' as columns, so we need to melt back:
pivot_melted = pivot_result.melt(id_vars=['right_index', 'city'], var_name='type', value_name='driver_count')

# Drop right_index as it's not needed in target
pivot_melted = pivot_melted.drop(columns=['right_index'])

# Join with df1 on city
merged = pd.merge(pivot_melted, df1[['city', 'fare', 'ride_id']], on='city', how='inner')

# Ensure correct dtypes
merged['type'] = merged['type'].astype(str)
merged['city'] = merged['city'].astype(str)
merged['fare'] = merged['fare'].astype(float)
merged['ride_id'] = merged['ride_id'].astype(float)
merged['driver_count'] = merged['driver_count'].astype('Int64')

merged = merged[['type', 'city', 'fare', 'ride_id', 'driver_count']]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_31/target_multisource_mcts.csv", index=False)