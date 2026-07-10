import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_82/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_82/training_1.csv", index_col=0)

df0_expanded = df0.assign(genres=df0['genres'].str.split('|')).explode('genres').rename(columns={'genres':'genres_single'})

df_merged = pd.merge(df1, df0_expanded[['movieId', 'title', 'genres_single']], on='movieId', how='inner')

df_merged = df_merged.rename(columns={'genres_single':'genres'})

df_merged['genres_arr'] = df0['genres'].str.split('|').reindex(df_merged['movieId']).values
df_merged['genres_arr'] = df_merged['genres_arr'].apply(lambda x: str(x) if isinstance(x, list) else '[]')

df_merged['genre_count'] = df_merged['genres_arr'].apply(lambda x: eval(x)[0] if (x != '[]' and len(eval(x))>0) else '')

df_merged = df_merged[['userId', 'movieId', 'rating', 'timestamp', 'title', 'genres', 'genres_arr', 'genre_count']]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_82/target_multisource_mcts.csv", index=False)