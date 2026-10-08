import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_82/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_82/training_1.csv", index_col=0)

df0_unpivoted = df0.assign(genres=df0['genres'].str.split('|')).explode('genres').reset_index(drop=True)

df_joined = pd.merge(df1, df0_unpivoted, on='movieId', how='inner')

df_joined['genres_arr'] = df_joined['genres'].str.split('|').apply(lambda x: str(x))
df_joined['genre_count'] = df_joined['genres'].str.split('|').str[0]

df_joined = df_joined[['userId', 'movieId', 'rating', 'timestamp', 'title', 'genres', 'genres_arr', 'genre_count']]

df_joined.to_csv("autopipeline-benchmarks/github-pipelines/length2_82/target_multisource_mcts.csv", index=False)