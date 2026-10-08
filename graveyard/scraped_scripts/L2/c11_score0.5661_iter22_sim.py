import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_1.csv", index_col=0)

df0_sub = df0[['city', 'driver_count', 'type']]
df1_sub = df1[['city', 'fare', 'ride_id']]

df0_pivot = df0_sub.pivot_table(index='city', columns='type', values='driver_count', aggfunc='sum').reset_index()
df0_pivot.columns.name = None

df_merged = pd.merge(df1_sub, df0_pivot, on='city', how='left')

if 'Urban' in df_merged.columns:
    df_merged['driver_count'] = df_merged['Urban'].fillna(0).astype(int)
else:
    df_merged['driver_count'] = 0

result = df_merged[['city', 'fare', 'ride_id', 'driver_count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_11/target_multisource_mcts.csv", index=False)