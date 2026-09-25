import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

df2_unpivot = df2.assign(genres_y=df2['genres'].str.split('|')).explode('genres_y').drop(columns=['genres']).rename(columns={'movie_id':'movie_id_y'})

joined_0 = pd.merge(df0, df1, on='user_id', how='inner')

final_df = pd.merge(joined_0, df2_unpivot, left_on='movie_id', right_on='movie_id_y', how='inner')

final_df = final_df.rename(columns={
    'movie_id': 'movie_id_x',
    'genres_y': 'genres_y'
})

final_df = final_df[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'movie_id_y', 'genres_y']]

final_df['title'] = pd.merge(df1[['movie_id']], df2[['movie_id', 'title']], left_on='movie_id', right_on='movie_id', how='left')['title']
final_df['genres_x'] = 0

final_df = final_df[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)