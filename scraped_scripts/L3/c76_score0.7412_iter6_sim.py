import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_76/training_1.csv", index_col=0)

agg = df1.groupby(['city']).agg(fare_avg=('fare', 'mean'), ride_count=('ride_id', 'count')).reset_index()

merged = pd.merge(df0, agg, how='inner', left_on=['city'], right_on=['city'])

result = merged.groupby(['type', 'city']).agg(fare=('fare_avg', 'mean')).reset_index()

result = result[['city', 'type', 'fare']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_76/target_multisource_mcts.csv", index=False)