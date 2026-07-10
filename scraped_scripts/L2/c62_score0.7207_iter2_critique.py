import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_62/training_1.csv", index_col=0)

# Join on city (inner join to keep only cities present in both sources)
df_joined = pd.merge(df0, df1, on='city', how='inner')

# Group by city and sum driver_count (in case of duplicates)
result = df_joined.groupby('city', as_index=False)['driver_count'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_62/target_multisource_mcts.csv", index=False)