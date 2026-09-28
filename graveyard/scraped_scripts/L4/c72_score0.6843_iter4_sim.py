import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

df0_sub = df0[['city', 'fare', 'ride_id']].copy()
df0_sub['a'] = df0_sub['fare']
df0_sub['b'] = 1
df0_sub = df0_sub[['city', 'a', 'b']]

df1_sub = df1[['city', 'driver_count']].copy()
df1_sub['a'] = df1_sub['driver_count'].astype(float)
df1_sub['b'] = 0
df1_sub = df1_sub[['city', 'a', 'b']]

union_df = pd.concat([df0_sub, df1_sub], ignore_index=True)

result = union_df.groupby('city', as_index=False).agg({'a':'mean', 'b':'sum'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)