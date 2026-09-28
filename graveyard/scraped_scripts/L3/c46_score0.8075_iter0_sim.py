import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_46/training_1.csv", index_col=0)

agg = df1.groupby('city').agg({'fare':'mean', 'ride_id':'count'}).reset_index()
agg.rename(columns={'fare':'Average Fare', 'ride_id':'Ride Count'}, inplace=True)

result = pd.merge(df0, agg, on='city', how='inner')

result = result[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_46/target_multisource_mcts.csv", index=False)