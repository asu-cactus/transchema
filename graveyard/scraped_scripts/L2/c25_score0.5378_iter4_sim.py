import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_1.csv", index_col=0)

df = pd.merge(df1, df0[['city', 'driver_count']], on='city', how='inner')

df = df[['city', 'fare', 'ride_id', 'driver_count']]

df['fare'] = df['fare'].astype(float)
df['ride_id'] = df['ride_id'].astype(float)
df['driver_count'] = df['driver_count'].astype(int)
df['city'] = df['city'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_25/target_multisource_mcts.csv", index=False)