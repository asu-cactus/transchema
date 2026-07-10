import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

df0['gender'] = df0['gender'].map({'M':1, 'F':0}).astype('Int64')
df0['zip'] = df0['zip'].str.extract(r'(\d+)').astype('Int64')

df = df1.merge(df0, on='user_id', how='left')
df = df.merge(df2, on='movie_id', how='left')

df = df.rename(columns={
    'genres': 'genres_y',
    'movie_id': 'movie_id_y'
})

df['title'] = df['title'].astype(str)
df['user_id'] = df['user_id'].astype('Int64')
df['movie_id_x'] = df['movie_id_y']
df['rating'] = df['rating'].astype('Int64')
df['timestamp'] = df['timestamp'].astype('Int64')
df['gender'] = df['gender'].astype('Int64')
df['age'] = df['age'].astype('Int64')
df['occupation'] = df['occupation'].astype('Int64')
df['zip'] = df['zip'].astype('Int64')
df['genres_x'] = 1

df = df[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)