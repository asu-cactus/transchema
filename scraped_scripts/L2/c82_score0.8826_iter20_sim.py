import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_82/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_82/training_1.csv", index_col=0)

df0_unpivoted = df0.assign(genres=df0['genres'].str.split('|')).explode('genres').rename(columns={'genres': 'genre_count'})

df_joined = pd.merge(df1, df0_unpivoted, on='movieId', how='inner')

group_cols = ['userId', 'movieId', 'timestamp', 'title', 'genre_count']
agg_df = df_joined.groupby(group_cols, as_index=False).agg({'rating':'mean'})

agg_df['genres'] = agg_df.groupby(['userId', 'movieId', 'timestamp', 'title'])['genre_count'].transform(lambda x: '|'.join(sorted(x.unique())))
agg_df['genres_arr'] = agg_df['genres'].apply(lambda x: str(x.split('|')))
agg_df['genre_count'] = agg_df['genre_count']

agg_df = agg_df[['userId', 'movieId', 'rating', 'timestamp', 'title', 'genres', 'genres_arr', 'genre_count']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_82/target_multisource_mcts.csv", index=False)