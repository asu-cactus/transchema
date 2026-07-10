import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_90/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_90/training_1.csv', index_col=0)

pivot_df = df0.pivot_table(index='city', values=['fare', 'ride_id'], aggfunc={'fare':'mean', 'ride_id':'max'}).reset_index()

merged = pd.merge(pivot_df, df1, on='city', how='inner')

agg = merged.groupby(['city', 'type']).agg({
    'fare': 'mean',
    'ride_id': ['max', 'count'],
    'driver_count': 'max'
}).reset_index()

agg.columns = ['city', 'City Type', 'Average Fare', 'ride_id', 'Total Number of Rides', 'Total Number of Drivers']

agg['Total Number of Rides'] = agg['Total Number of Rides'].astype(int)
agg['Total Number of Drivers'] = agg['Total Number of Drivers'].astype(int)

agg.to_csv('autopipeline-benchmarks/github-pipelines/length5_90/target_multisource_mcts.csv', index=False)