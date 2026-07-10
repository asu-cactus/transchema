import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_69/training_1.csv", index_col=0)

groupby_result = df1.groupby('date').agg({'city':'first', 'fare':'mean', 'ride_id':'first'}).reset_index()

merged = pd.merge(df0, groupby_result, how='inner', left_on='city', right_on='city')

result = merged[['city', 'driver_count', 'type', 'date', 'fare', 'ride_id']]

result['driver_count'] = result['driver_count'].astype(int)
result['fare'] = result['fare'].astype(float)
result['ride_id'] = result['ride_id'].astype(int)
result['date'] = result['date'].astype(str)
result['city'] = result['city'].astype(str)
result['type'] = result['type'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_69/target_multisource_mcts.csv", index=False)