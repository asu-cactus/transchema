import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_45/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_45/training_1.csv", index_col=0)

pivot_df = df0.pivot_table(index='city', values='fare', aggfunc='mean').reset_index()
ride_counts = df0.groupby('city')['ride_id'].count().reset_index().rename(columns={'ride_id': 'Ride Count'})
pivot_df = pivot_df.merge(ride_counts, on='city')

merged = pivot_df.merge(df1, on='city')

result = merged.rename(columns={'fare': 'Average Fare', 'driver_count': 'driver_count', 'type': 'type', 'city': 'city', 'Ride Count': 'Ride Count'})

result = result[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_45/target_multisource_mcts.csv", index=False)