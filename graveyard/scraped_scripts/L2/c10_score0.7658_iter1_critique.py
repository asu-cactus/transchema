import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_1.csv", index_col=0)

# Join on 'city'
df = pd.merge(df0, df1, on='city', how='inner')

# Group by 'city' and sum 'driver_count'
df_grouped = df.groupby('city', as_index=False).agg({'driver_count': 'sum'})

# Ensure driver_count is int type
df_grouped['driver_count'] = df_grouped['driver_count'].astype(int)

# Output only the target columns
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_10/target_multisource_mcts.csv", index=False)