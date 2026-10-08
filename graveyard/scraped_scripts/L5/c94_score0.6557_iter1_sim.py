import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_1.csv", index_col=0)

pivot = df1.pivot_table(index='city', values=['fare', 'ride_id'], aggfunc={'fare':'mean', 'ride_id':['mean', 'count']})
pivot.columns = ['Average Fare', 'ride_id', 'Total Number of Rides']
pivot = pivot.reset_index()

merged = pd.merge(pivot, df0, how='inner', left_on='city', right_on='city')

merged = merged.rename(columns={
    'city': 'City',
    'type': 'City Type',
    'driver_count': 'Total Number of Drivers'
})

result = merged[['City', 'Average Fare', 'ride_id', 'Total Number of Rides', 'City Type', 'Total Number of Drivers']]

result['Total Number of Rides'] = result['Total Number of Rides'].astype(int)
result['Total Number of Drivers'] = result['Total Number of Drivers'].astype(int)
result['Average Fare'] = result['Average Fare'].astype(float)
result['ride_id'] = result['ride_id'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_94/target_multisource_mcts.csv", index=False)