import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_46/training_1.csv", index_col=0)

agg_df1 = df1.groupby('city').agg(
    Average_Fare=('fare', 'mean'),
    Ride_Count=('ride_id', 'count')
).reset_index()

agg_df0 = df0.groupby(['type', 'city']).agg(
    driver_count=('driver_count', 'sum')
).reset_index()

merged = pd.merge(agg_df0, agg_df1, how='inner', on='city')

result = merged[['city', 'driver_count', 'type', 'Average_Fare', 'Ride_Count']]

result['driver_count'] = result['driver_count'].astype(int)
result['Ride_Count'] = result['Ride_Count'].astype(int)
result['Average_Fare'] = result['Average_Fare'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_46/target_multisource_mcts.csv", index=False)