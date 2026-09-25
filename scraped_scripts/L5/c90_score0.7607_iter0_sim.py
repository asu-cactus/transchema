import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_90/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_90/training_1.csv", index_col=0)

agg = df0.groupby('city').agg({
    'fare': 'mean',
    'ride_id': ['count', 'mean']
}).reset_index()
agg.columns = ['city', 'Average Fare', 'Total Number of Rides', 'ride_id']

merged = pd.merge(agg, df1, how='inner', left_on='city', right_on='city')

merged = merged.rename(columns={
    'type': 'City Type',
    'driver_count': 'Total Number of Drivers'
})

merged['Total Number of Rides'] = merged['Total Number of Rides'].astype(int)
merged['Total Number of Drivers'] = merged['Total Number of Drivers'].astype(int)
merged['Average Fare'] = merged['Average Fare'].astype(float)
merged['ride_id'] = merged['ride_id'].astype(float)
merged['City'] = merged['city']
result = merged[['City', 'Average Fare', 'ride_id', 'Total Number of Rides', 'City Type', 'Total Number of Drivers']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_90/target_multisource_mcts.csv", index=False)