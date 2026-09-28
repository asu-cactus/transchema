import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_16/training_1.csv", index_col=0)

# Join on 'city'
df_joined = pd.merge(df1, df0[['city', 'driver_count']], on='city', how='inner')

# Group by 'city' and 'driver_count', aggregate fare and ride_id by mean
df_grouped = df_joined.groupby(['city', 'driver_count'], as_index=False).agg({
    'fare': 'mean',
    'ride_id': 'mean'
})

# Ensure correct dtypes
df_grouped['city'] = df_grouped['city'].astype(str)
df_grouped['driver_count'] = df_grouped['driver_count'].astype('Int64')
df_grouped['fare'] = pd.to_numeric(df_grouped['fare'], errors='coerce')
df_grouped['ride_id'] = pd.to_numeric(df_grouped['ride_id'], errors='coerce')

# Reorder columns to match target schema
df_grouped = df_grouped[['city', 'fare', 'ride_id', 'driver_count']]

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_16/target_multisource_mcts.csv", index=False)