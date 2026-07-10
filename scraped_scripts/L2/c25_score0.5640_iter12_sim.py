import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_1.csv", index_col=0)

merged = pd.merge(source1, source0[['city', 'driver_count']], on='city', how='left')

merged['driver_count'] = merged['driver_count'].astype('Int64')
merged['fare'] = merged['fare'].astype(float)
merged['ride_id'] = merged['ride_id'].astype(float)
merged['city'] = merged['city'].astype(str)

result = merged[['city', 'fare', 'ride_id', 'driver_count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_25/target_multisource_mcts.csv", index=False)