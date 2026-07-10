import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_44/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_44/training_1.csv", index_col=0)

merged = pd.merge(df0, df1[['city']], on='city', how='inner')

grouped = merged.groupby('city', as_index=False).agg({'fare': 'mean', 'ride_id': 'min'})

grouped['ride_id'] = grouped['ride_id'].astype(int)
grouped['fare'] = grouped['fare'].astype(float)
grouped['city'] = grouped['city'].astype(str)

grouped[['city', 'fare', 'ride_id']].to_csv("autopipeline-benchmarks/github-pipelines/length2_44/target_multisource_mcts.csv", index=False)