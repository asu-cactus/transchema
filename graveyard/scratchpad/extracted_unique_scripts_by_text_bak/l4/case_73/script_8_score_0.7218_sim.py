import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv', index_col=0)

grouped = df0.groupby('city').agg({'fare':'mean', 'ride_id':'count'}).reset_index()
grouped.rename(columns={'city':'City', 'fare':'Average Fare ($)', 'ride_id':'Number of Rides'}, inplace=True)

df1.rename(columns={'city':'City', 'driver_count':'Number of Drivers', 'type':'City Type'}, inplace=True)

result = pd.merge(grouped, df1, on='City', how='inner')

result = result.astype({'City': str, 'Average Fare ($)': float, 'Number of Rides': float, 'Number of Drivers': int, 'City Type': str})

result.to_csv('autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv', index=False)