import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_69/training_1.csv", index_col=0)

# Join Source0 and Source1 on 'city'
df_joined = pd.merge(df0, df1[['city']], on='city', how='inner')

# Group by 'city' and aggregate driver_count by max (driver_count is constant per city)
df_result = df_joined.groupby('city', as_index=False).agg({'driver_count': 'max'})

# Ensure driver_count is int
df_result['driver_count'] = df_result['driver_count'].astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length2_69/target_multisource_mcts.csv", index=False)