import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_44/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_44/training_1.csv", index_col=0)

grouped = df0.groupby(['city', 'ride_id'], as_index=False).agg({'fare':'mean'})

merged = pd.merge(grouped, df1[['city']], on='city', how='inner')

merged['ride_id'] = merged['ride_id'].astype(int)
merged['fare'] = merged['fare'].astype(float)
merged['city'] = merged['city'].astype(str)

merged[['city', 'fare', 'ride_id']].to_csv("autopipeline-benchmarks/github-pipelines/length2_44/target_multisource_mcts.csv", index=False)