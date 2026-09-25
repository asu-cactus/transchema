import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv', index_col=0)

df0.rename(columns={'city': 'City', 'fare': 'Average Fare ($)', 'ride_id': 'ride_id'}, inplace=True)
df1.rename(columns={'city': 'City', 'driver_count': 'Number of Drivers', 'type': 'City Type'}, inplace=True)

merged = pd.merge(df0, df1, on='City', how='inner')

grouped = merged.groupby(['City', 'Number of Drivers', 'City Type']).agg({
    'Average Fare ($)': 'mean',
    'ride_id': 'count'
}).reset_index()

grouped.rename(columns={'ride_id': 'Number of Rides'}, inplace=True)

grouped = grouped.astype({
    'City': str,
    'Average Fare ($)': float,
    'Number of Rides': float,
    'Number of Drivers': int,
    'City Type': str
})

grouped.to_csv('autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv', index=False)