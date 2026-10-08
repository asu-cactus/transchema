import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

agg = df0.groupby('city').agg(
    Average_Fare=('fare', 'mean'),
    Number_of_Rides=('ride_id', 'count')
).reset_index()

driver_sum = df1.groupby(['city', 'type']).agg(
    Number_of_Drivers=('driver_count', 'sum')
).reset_index()

merged = pd.merge(agg, driver_sum, on='city', how='inner')

merged = merged.rename(columns={
    'city': 'City',
    'Average_Fare': 'Average Fare ($)',
    'Number_of_Rides': 'Number of Rides',
    'Number_of_Drivers': 'Number of Drivers',
    'type': 'City Type'
})

merged['Number of Drivers'] = merged['Number of Drivers'].astype('Int64')

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)