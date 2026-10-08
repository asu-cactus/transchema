import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_73/test_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_73/test_1.csv', index_col=0)

grouped = df0.groupby('city').agg({'fare': 'mean', 'ride_id': 'count'}).reset_index()
grouped.rename(columns={'fare': 'Average Fare ($)', 'ride_id': 'Number of Rides', 'city': 'City'}, inplace=True)
grouped['Number of Rides'] = grouped['Number of Rides'].astype(float)

df1.rename(columns={'driver_count': 'Number of Drivers', 'type': 'City Type'}, inplace=True)

merged = pd.merge(grouped, df1, left_on='City', right_on='city')

merged.drop(columns='city', inplace=True)
merged.to_csv('autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts_recovery_test_val.csv', index=False)