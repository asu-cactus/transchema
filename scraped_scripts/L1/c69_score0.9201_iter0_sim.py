import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_69/training_1.csv", index_col=0)

groupby_result = df1.groupby('date').agg({
    'city': 'first',
    'fare': 'mean',
    'ride_id': 'first'
}).reset_index()

joined = pd.merge(df0, groupby_result, how='inner', left_on='city', right_on='city')

joined['date'] = joined['date'].astype(str)
joined['fare'] = joined['fare'].astype(float)
joined['ride_id'] = joined['ride_id'].astype(int)
joined['driver_count'] = joined['driver_count'].astype(int)
joined['city'] = joined['city'].astype(str)
joined['type'] = joined['type'].astype(str)

result = joined[['city', 'driver_count', 'type', 'date', 'fare', 'ride_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_69/target_multisource_mcts.csv", index=False)