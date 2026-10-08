import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="city")

df = df[['city', 'driver_count', 'type', 'date', 'fare', 'ride_id']]

df['driver_count'] = df['driver_count'].astype('Int64')
df['fare'] = df['fare'].astype(float)
df['ride_id'] = df['ride_id'].astype('Int64')
df['date'] = df['date'].astype(str)
df['city'] = df['city'].astype(str)
df['type'] = df['type'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_7/target_multisource_mcts.csv", index=False)