import pandas as pd

df_users = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_0.csv", index_col=0)
df_movies = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_1.csv", index_col=0)
df_ratings = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_2.csv", index_col=0)

# UNPIVOT step: The source 2 (df_ratings) is already in long format with columns user_id, movie_id, rating, timestamp
# So no unpivot needed on df_ratings itself.
# The partial plan suggests unpivot, but here the only candidate for unpivot is genres in df_movies, but target schema does not require genres.
# So we skip unpivot on genres as target schema does not have genres.
# The partial plan likely refers to unpivoting ratings if they were wide, but here ratings are already long.
# So we interpret the partial plan as starting from df_ratings as is.

# Join ratings with movies on movie_id to get title
joined_1 = pd.merge(df_ratings, df_movies[['movie_id', 'title']], on='movie_id', how='left')

# Join the above with users on user_id to get age and occupation
joined_2 = pd.merge(joined_1, df_users[['user_id', 'age', 'occupation']], on='user_id', how='left')

# Select and reorder columns to match target schema
result = joined_2[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

# Convert data types to match target schema
result['title'] = result['title'].astype(str)
result['user_id'] = result['user_id'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_18/target_multisource_mcts.csv", index=False)