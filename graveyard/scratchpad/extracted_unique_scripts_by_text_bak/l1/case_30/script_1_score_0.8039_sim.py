import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_30/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_30/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="movieId", how="inner")

df = df[['movieId', 'title', 'genres', 'userId', 'tag', 'timestamp']]

df['movieId'] = df['movieId'].astype(int)
df['userId'] = df['userId'].astype(int)
df['timestamp'] = df['timestamp'].astype(int)
df['title'] = df['title'].astype(str)
df['genres'] = df['genres'].astype(str)
df['tag'] = df['tag'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_30/target_multisource_mcts.csv", index=False)