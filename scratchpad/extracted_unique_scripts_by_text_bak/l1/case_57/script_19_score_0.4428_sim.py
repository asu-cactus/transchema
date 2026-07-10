import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_57/training_0.csv", index_col=0)
df_target = df0[['movieId', 'rating']].copy()
df_target['movieId'] = df_target['movieId'].astype(int)
df_target['rating'] = df_target['rating'].astype(float)
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_57/target_multisource_mcts.csv", index=False)