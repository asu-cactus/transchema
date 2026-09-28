import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_80/training_0.csv", index_col=0)
df = pd.concat([df0], ignore_index=True)
df = df[['movieId', 'rating']]
df['movieId'] = df['movieId'].astype(int)
df['rating'] = df['rating'].astype(float)
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)