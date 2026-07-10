import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_1.csv", index_col=0)

merged = pd.merge(df1, df0[['city', 'driver_count']], on='city', how='inner')

agg_df = merged.groupby('city', as_index=False).agg({
    'fare': 'mean',
    'ride_id': 'mean',
    'driver_count': 'first'
})

agg_df['fare'] = agg_df['fare'].astype(float)
agg_df['ride_id'] = agg_df['ride_id'].astype(float)
agg_df['driver_count'] = agg_df['driver_count'].astype(int)
agg_df['city'] = agg_df['city'].astype(str)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_11/target_multisource_mcts.csv", index=False)