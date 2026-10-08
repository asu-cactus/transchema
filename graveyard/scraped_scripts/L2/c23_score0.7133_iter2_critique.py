import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_1.csv", index_col=0)

# Join on 'city'
df_joined = pd.merge(df0[['city']], df1, on='city', how='inner')

# Group by 'city' and sum 'driver_count' as 'type'
agg = df_joined.groupby('city', as_index=False)['driver_count'].sum()

# Rename 'driver_count' to 'type' to match target schema
agg = agg.rename(columns={'driver_count': 'type'})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_23/target_multisource_mcts.csv", index=False)