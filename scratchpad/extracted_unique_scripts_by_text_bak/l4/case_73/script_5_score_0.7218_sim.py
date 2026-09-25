import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

agg = df0.groupby('city').agg({'fare':'mean', 'ride_id':'count'}).reset_index()
agg.rename(columns={'fare':'Average Fare ($)', 'ride_id':'Number of Rides', 'city':'City'}, inplace=True)

joined = pd.merge(agg, df1, how='inner', left_on='City', right_on='city')
joined.rename(columns={'driver_count':'Number of Drivers', 'type':'City Type'}, inplace=True)

result = joined[['City', 'Average Fare ($)', 'Number of Rides', 'Number of Drivers', 'City Type']].copy()
result['Number of Drivers'] = result['Number of Drivers'].astype('Int64')
result['Average Fare ($)'] = result['Average Fare ($)'].astype(float)
result['Number of Rides'] = result['Number of Rides'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)