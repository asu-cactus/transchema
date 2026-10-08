import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_31/training_1.csv", index_col=0)

# Join on 'city'
merged = pd.merge(df0, df1, on='city', how='inner')

# Group by 'type' and 'city'
agg_df = merged.groupby(['type', 'city'], as_index=False).agg({
    'fare': 'mean',
    'ride_id': 'mean',
    'driver_count': 'sum'
})

# Ensure correct dtypes
agg_df['type'] = agg_df['type'].astype(str)
agg_df['city'] = agg_df['city'].astype(str)
agg_df['fare'] = agg_df['fare'].astype(float)
agg_df['ride_id'] = agg_df['ride_id'].astype(float)
agg_df['driver_count'] = agg_df['driver_count'].astype('Int64')

agg_df = agg_df[['type', 'city', 'fare', 'ride_id', 'driver_count']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_31/target_multisource_mcts.csv", index=False)