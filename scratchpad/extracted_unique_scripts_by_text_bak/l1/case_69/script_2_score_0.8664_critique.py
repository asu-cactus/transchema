import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_69/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, how='inner', on='city')

result = merged[['city', 'driver_count', 'type', 'date', 'fare', 'ride_id']]

result['driver_count'] = result['driver_count'].astype(int)
result['fare'] = result['fare'].astype(float)
result['ride_id'] = result['ride_id'].astype(int)
result['date'] = result['date'].astype(str)
result['city'] = result['city'].astype(str)
result['type'] = result['type'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_69/target_multisource_mcts.csv", index=False)