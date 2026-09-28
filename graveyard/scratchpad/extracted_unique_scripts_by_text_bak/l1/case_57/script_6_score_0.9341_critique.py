import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_57/training_0.csv", index_col=0)
df0['movieId'] = df0['movieId'].astype(int)
df0['rating'] = df0['rating'].astype(float)

df_target = df0.groupby('movieId', as_index=False).agg({'rating': 'mean'})

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_57/target_multisource_mcts.csv", index=False)