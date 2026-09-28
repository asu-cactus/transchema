import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

agg_df0 = df0.groupby('city', as_index=False)['fare'].mean().rename(columns={'fare': 'average_fare'})
agg_df1 = df1.groupby(['city', 'type'], as_index=False)['driver_count'].sum()

grouped = pd.merge(agg_df1, agg_df0, on='city', how='inner')

result = grouped[['city', 'driver_count', 'type', 'average_fare']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)