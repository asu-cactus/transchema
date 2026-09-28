import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

df0['gender'] = df0['gender'].map({'M':1, 'F':2}).fillna(0).astype(int)
df0['zip'] = df0['zip'].str.extract('(\d+)').astype(float).fillna(0).astype(int)

df_joined_1 = pd.merge(df1, df2, on='movie_id', how='inner')

df_final = pd.merge(df_joined_1, df0, on='user_id', how='inner')

df_final = df_final.rename(columns={
    'movie_id': 'movie_id_x',
    'genres': 'genres_y'
})

df_final['movie_id_y'] = df_final['movie_id_x']
df_final['genres_x'] = 1

df_final = df_final[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)