import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

agg_fare = source0.groupby('city')['fare'].mean().reset_index(name='Average Fare ($)')
agg_rides = source0.groupby('city')['ride_id'].count().reset_index(name='Number of Rides')
agg_drivers = source1.groupby('city')['driver_count'].sum().reset_index(name='Number of Drivers')
agg_type = source1.groupby('city')['type'].max().reset_index(name='City Type')

df = agg_fare.merge(agg_rides, on='city', how='inner')
df = df.merge(agg_drivers, on='city', how='inner')
df = df.merge(agg_type, on='city', how='inner')

df.rename(columns={'city': 'City'}, inplace=True)
df['Number of Drivers'] = df['Number of Drivers'].astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)