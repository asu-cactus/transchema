import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_2.csv", index_col=0)

# Join ratings with user info on user_id
df_ratings_users = pd.merge(df2, df0[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Join above with movie info on movie_id
df_full = pd.merge(df_ratings_users, df1[['movie_id', 'title']], on='movie_id', how='inner')

# Group by title and movie_id, aggregate means of user_id, age, occupation, rating, timestamp
final = df_full.groupby(['title', 'movie_id'], as_index=False).agg({
    'user_id': 'mean',
    'age': 'mean',
    'occupation': 'mean',
    'rating': 'mean',
    'timestamp': 'mean'
})

# Reorder columns to match target schema
final = final[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_3/target_multisource_mcts.csv", index=False)