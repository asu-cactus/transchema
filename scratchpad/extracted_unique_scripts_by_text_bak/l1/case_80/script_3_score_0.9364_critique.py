import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_80/training_0.csv", index_col=0)
df0['movieId'] = df0['movieId'].astype(int)
df0['rating'] = df0['rating'].astype(float)

df = df0.groupby('movieId', as_index=False)['rating'].mean()

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)