import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_18/training_0.csv", index_col=0)
df = df0[['city', 'fare', 'ride_id']].copy()
df['city'] = df['city'].astype(str)
df['fare'] = df['fare'].astype(float)
df['ride_id'] = df['ride_id'].astype(int)
df.to_csv("autopipeline-benchmarks/github-pipelines/length2_18/target_multisource_mcts.csv", index=False)