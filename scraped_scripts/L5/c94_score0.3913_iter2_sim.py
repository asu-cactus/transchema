import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_1.csv", index_col=0)

agg1 = df1.groupby('city').agg(
    Average_Fare=('fare', 'mean'),
    Count_of_ride_id=('ride_id', 'count')
).reset_index()

join_df = pd.merge(df0, agg1, how='inner', left_on='city', right_on='city')

agg2 = join_df.groupby(['city', 'type']).agg(
    Sum_of_driver_count=('driver_count', 'sum'),
    Average_Fare=('Average_Fare', 'max'),
    Count_of_ride_id=('Count_of_ride_id', 'max')
).reset_index()

agg2 = agg2.rename(columns={
    'city': 'City',
    'Average_Fare': 'Average Fare',
    'Count_of_ride_id': 'Total Number of Rides',
    'type': 'City Type',
    'Sum_of_driver_count': 'Total Number of Drivers'
})

agg2['ride_id'] = float('nan')

agg2 = agg2.astype({
    'City': str,
    'Average Fare': float,
    'ride_id': float,
    'Total Number of Rides': int,
    'City Type': str,
    'Total Number of Drivers': int
})

agg2.to_csv("autopipeline-benchmarks/github-pipelines/length5_94/target_multisource_mcts.csv", index=False)