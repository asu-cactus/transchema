import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/training_1.csv", index_col=0)

agg = df1.groupby('city').agg(fare=('fare', 'mean'), ride_id=('ride_id', 'count')).reset_index()

agg = agg.rename(columns={'fare': 'fare_avg', 'ride_id': 'ride_id_count'})

grouped_0 = df0.groupby(['type', 'city'], as_index=False).agg(driver_count_sum=('driver_count', 'sum'))

join1 = pd.merge(grouped_0, agg, how='inner', left_on='city', right_on='city')

final = pd.merge(join1, df1, how='inner', left_on='city', right_on='city')

final['driver_count'] = final['driver_count_sum'].astype(int)
final['fare'] = final['fare_avg'].astype(float)
final['ride_id'] = final['ride_id_count'].astype(int)

final = final[['city', 'driver_count', 'type', 'date', 'fare', 'ride_id']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length1_7/target_multisource_mcts.csv", index=False)