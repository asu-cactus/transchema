import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

agg_fare = source0.groupby('city')['fare'].min().reset_index(name='min_fare')
agg_rides = source0.groupby('city')['ride_id'].nunique().reset_index(name='num_rides')

agg_source0 = pd.merge(agg_fare, agg_rides, on='city')

agg_driver_count = source1.groupby('city')['driver_count'].max().reset_index(name='max_driver_count')
agg_type = source1.groupby('city')['type'].max().reset_index(name='max_type')

agg_source1 = pd.merge(agg_driver_count, agg_type, on='city')

merged = pd.merge(agg_source1, agg_source0, on='city', how='inner')

result = pd.DataFrame()
result['City'] = merged['city']
result['Average Fare ($)'] = merged['min_fare'].astype(float)
result['Number of Rides'] = merged['num_rides'].astype(float)
result['Number of Drivers'] = merged['max_driver_count'].astype(int)
result['City Type'] = merged['max_type'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)