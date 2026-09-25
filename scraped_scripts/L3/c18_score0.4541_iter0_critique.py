import pandas as pd

df_users = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_0.csv", index_col=0)
df_movies = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_1.csv", index_col=0)
df_ratings = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_2.csv", index_col=0)

# Join ratings with users on user_id
df_merged = df_ratings.merge(df_users, on='user_id', how='inner')

# Join the above with movies on movie_id
df_merged = df_merged.merge(df_movies[['movie_id', 'title']], on='movie_id', how='inner')

# Select and reorder columns as per target schema
df_result = df_merged[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

# Cast columns to target types
df_result['user_id'] = df_result['user_id'].astype(float)
df_result['movie_id'] = df_result['movie_id'].astype(int)
df_result['rating'] = df_result['rating'].astype(float)
df_result['timestamp'] = df_result['timestamp'].astype(float)
df_result['age'] = df_result['age'].astype(float)
df_result['occupation'] = df_result['occupation'].astype(float)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length3_18/target_multisource_mcts.csv", index=False)