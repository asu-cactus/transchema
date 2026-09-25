import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

# Join on 'track_id' to combine index_track and dummy columns
df_joined = pd.merge(df1, df0[['track_id', 'dummy']], on='track_id', how='inner')

# Group by index_track and track_id, aggregate dummy by max (dummy is always 1, so max or sum is fine)
df_grouped = df_joined.groupby(['index_track', 'track_id'], as_index=False).agg({'dummy': 'max'})

# Ensure correct dtypes as per target schema
df_grouped['index_track'] = df_grouped['index_track'].astype('Int64')
df_grouped['track_id'] = df_grouped['track_id'].astype('Int64')
df_grouped['dummy'] = df_grouped['dummy'].astype('Int64')

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)