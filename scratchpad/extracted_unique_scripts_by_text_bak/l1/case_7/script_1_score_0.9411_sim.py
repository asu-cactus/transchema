import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, how="inner", on="city")

merged = merged[['city', 'driver_count', 'type', 'date', 'fare', 'ride_id']]

merged['driver_count'] = merged['driver_count'].astype(int)
merged['fare'] = merged['fare'].astype(float)
merged['ride_id'] = merged['ride_id'].astype(int)
merged['date'] = merged['date'].astype(str)
merged['city'] = merged['city'].astype(str)
merged['type'] = merged['type'].astype(str)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_7/target_multisource_mcts.csv", index=False)