import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_82/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_82/training_1.csv", index_col=0)

df = pd.merge(df1, df0, on="movieId", how="inner")

df['genres_arr'] = df['genres'].str.split('|')
df['genre_count'] = df['genres_arr'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)

df = df[['userId', 'movieId', 'rating', 'timestamp', 'title', 'genres', 'genres_arr', 'genre_count']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_82/target_multisource_mcts.csv")