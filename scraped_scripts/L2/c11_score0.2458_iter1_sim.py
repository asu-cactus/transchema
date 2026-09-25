import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_1.csv", index_col=0)

df0_sub = df0[['city', 'driver_count']].copy()
df0_sub['fare'] = pd.NA
df0_sub['ride_id'] = pd.NA

df1_sub = df1[['city', 'fare', 'ride_id']].copy()
df1_sub['driver_count'] = pd.NA

df_union = pd.concat([df0_sub, df1_sub], ignore_index=True)

df_union['city'] = df_union['city'].astype(str)
df_union['fare'] = pd.to_numeric(df_union['fare'], errors='coerce')
df_union['ride_id'] = pd.to_numeric(df_union['ride_id'], errors='coerce')
df_union['driver_count'] = pd.to_numeric(df_union['driver_count'], errors='coerce').astype('Int64')

df_union = df_union[['city', 'fare', 'ride_id', 'driver_count']]

df_union.to_csv("autopipeline-benchmarks/github-pipelines/length2_11/target_multisource_mcts.csv", index=False)