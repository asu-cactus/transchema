import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_57/training_0.csv", index_col=0)
df = df0[['movieId', 'rating']].copy()
df['movieId'] = df['movieId'].astype(int)
df['rating'] = df['rating'].astype(float)
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_57/target_multisource_mcts.csv", index=False)