import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

agg1 = source1.groupby(['city', 'type'], as_index=False)['driver_count'].sum()
agg0 = source0.groupby('city', as_index=False)['fare'].mean().rename(columns={'fare': 'average_fare'})

result = pd.merge(agg1, agg0, how='inner', on='city')

result = result[['city', 'driver_count', 'type', 'average_fare']]
result['driver_count'] = result['driver_count'].astype(int)
result['average_fare'] = result['average_fare'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)