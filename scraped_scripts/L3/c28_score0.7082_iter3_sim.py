import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_28/training_1.csv", index_col=0)

agg_df0 = df0.groupby(['type', 'city'], as_index=False)['driver_count'].sum()
agg_df1 = df1.groupby('city', as_index=False).agg({'fare':'mean', 'ride_id':'count'}).rename(columns={'fare':'Average Fare', 'ride_id':'Ride Count'})

result = pd.merge(agg_df0, agg_df1, how='inner', on='city')

result = result[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_28/target_multisource_mcts.csv", index=False)