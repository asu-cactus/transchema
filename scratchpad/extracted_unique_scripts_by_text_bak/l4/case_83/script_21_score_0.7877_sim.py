import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

pivot_result = source0.pivot_table(index='city', columns='date', values='fare', aggfunc='mean').reset_index()
pivot_result['average_fare'] = pivot_result.drop(columns='city').mean(axis=1)
pivot_result = pivot_result[['city', 'average_fare']]

merged = pd.merge(pivot_result, source1, on='city', how='inner')

result = merged.groupby(['city', 'driver_count', 'type'], as_index=False).agg({'average_fare':'mean'})

result['driver_count'] = result['driver_count'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)