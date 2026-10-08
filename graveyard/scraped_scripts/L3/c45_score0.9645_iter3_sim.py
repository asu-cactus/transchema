import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_45/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_45/training_1.csv", index_col=0)

df0['type'] = 'Urban'
grouped = df0.groupby(['city', 'type']).agg(
    Ride_Count=('ride_id', 'count'),
    Average_Fare=('fare', 'mean')
).reset_index()

result = pd.merge(grouped, df1, on=['city', 'type'], how='inner')

result = result.rename(columns={
    'Ride_Count': 'Ride Count',
    'Average_Fare': 'Average Fare',
    'driver_count': 'driver_count',
    'city': 'city',
    'type': 'type'
})

result = result[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_45/target_multisource_mcts.csv", index=False)