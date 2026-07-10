import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

grouped = df0.groupby('city', as_index=False)['fare'].mean().rename(columns={'fare': 'average_fare'})

merged = pd.merge(df1, grouped, how='inner', on='city')

merged['driver_count'] = merged['driver_count'].astype(int)
merged['type'] = merged['type'].astype(str)
merged['city'] = merged['city'].astype(str)
merged['average_fare'] = merged['average_fare'].astype(float)

merged = merged[['city', 'driver_count', 'type', 'average_fare']]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)