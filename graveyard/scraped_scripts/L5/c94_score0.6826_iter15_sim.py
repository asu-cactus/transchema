import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_1.csv", index_col=0)

agg = df1.groupby('city').agg(
    min_fare=('fare', 'min'),
    max_fare=('fare', 'max'),
    total_rides=('ride_id', 'count')
).reset_index()

max_driver = df0.groupby('city').agg(
    max_driver_count=('driver_count', 'max'),
    city_type=('type', 'first')
).reset_index()

merged = pd.merge(agg, max_driver, on='city', how='inner')

merged['Average Fare'] = (merged['min_fare'] + merged['max_fare']) / 2
merged['City'] = merged['city']
merged['ride_id'] = merged['total_rides'].astype(float)
merged['Total Number of Rides'] = merged['total_rides'].astype(int)
merged['City Type'] = merged['city_type']
merged['Total Number of Drivers'] = merged['max_driver_count'].astype(int)

result = merged[['City', 'Average Fare', 'ride_id', 'Total Number of Rides', 'City Type', 'Total Number of Drivers']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_94/target_multisource_mcts.csv", index=False)