import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_99/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_99/training_1.csv", index_col=0)

# Inner join on city to keep only cities present in both sources
joined = pd.merge(df0, df1[['city']], on='city', how='inner')

# Group by city and sum driver_count
result = joined.groupby('city', as_index=False)['driver_count'].sum()

result['driver_count'] = result['driver_count'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_99/target_multisource_mcts.csv", index=False)