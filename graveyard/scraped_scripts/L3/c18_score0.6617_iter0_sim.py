import pandas as pd

df_users = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_0.csv", index_col=0)
df_movies = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_1.csv", index_col=0)
df_ratings = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_2.csv", index_col=0)

df_merged = df_ratings.merge(df_movies[['movie_id', 'title']], on='movie_id', how='inner')

agg = df_merged.groupby('title').agg(
    user_id=('user_id', 'mean'),
    movie_id=('movie_id', 'mean'),
    rating=('rating', 'mean'),
    timestamp=('timestamp', 'mean')
).reset_index()

agg = agg.merge(df_users[['user_id', 'age', 'occupation']], on='user_id', how='inner')

agg = agg[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

agg['user_id'] = agg['user_id'].astype(float)
agg['movie_id'] = agg['movie_id'].astype(int)
agg['rating'] = agg['rating'].astype(float)
agg['timestamp'] = agg['timestamp'].astype(float)
agg['age'] = agg['age'].astype(float)
agg['occupation'] = agg['occupation'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_18/target_multisource_mcts.csv", index=False)