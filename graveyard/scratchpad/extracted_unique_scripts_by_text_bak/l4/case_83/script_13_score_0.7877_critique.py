import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

# Join on city
merged = pd.merge(df0, df1, on='city', how='inner')

# Group by city, driver_count, type and aggregate average fare
result = merged.groupby(['city', 'driver_count', 'type'], as_index=False)['fare'].mean().rename(columns={'fare': 'average_fare'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)