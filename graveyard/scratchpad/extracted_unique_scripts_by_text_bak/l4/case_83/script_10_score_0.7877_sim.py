import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

pivot_result = df0.pivot_table(index='city', values='fare', aggfunc='mean').reset_index()
pivot_result = pivot_result.rename(columns={'fare': 'average_fare'})

merged = pd.merge(pivot_result, df1, on='city')

result = merged[['city', 'driver_count', 'type', 'average_fare']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)