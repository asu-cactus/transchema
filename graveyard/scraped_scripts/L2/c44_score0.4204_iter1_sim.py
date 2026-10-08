import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_44/training_0.csv", index_col=0)

df_target = df0[['city', 'fare', 'ride_id']].copy()
df_target['city'] = df_target['city'].astype(str)
df_target['fare'] = df_target['fare'].astype(float)
df_target['ride_id'] = df_target['ride_id'].astype(int)

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length2_44/target_multisource_mcts.csv", index=False)