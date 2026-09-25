import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_29/training_1.csv", index_col=0)

agg = df1.groupby('city').agg(
    Average_Fare=('fare', 'mean'),
    Ride_Count=('ride_id', 'count')
).reset_index()

driver_sum = df0.groupby(['type', 'city'], as_index=False).agg(driver_count=('driver_count', 'sum'))

merged = pd.merge(driver_sum, agg, how='inner', left_on=['city'], right_on=['city'])

result = merged[['city', 'driver_count', 'type', 'Average_Fare', 'Ride_Count']]

result.rename(columns={'Average_Fare': 'Average Fare', 'Ride_Count': 'Ride Count'}, inplace=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_29/target_multisource_mcts.csv", index=False)