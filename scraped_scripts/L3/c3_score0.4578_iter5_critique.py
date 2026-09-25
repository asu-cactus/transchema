import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_2.csv", index_col=0)

# Join ratings with user info on user_id
merged = pd.merge(df2, df0[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Join the above with movie info on movie_id
merged = pd.merge(merged, df1[['movie_id', 'title']], on='movie_id', how='inner')

# Select and reorder columns as per target schema
result = merged[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']]

# Cast columns to target types
result['user_id'] = result['user_id'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_3/target_multisource_mcts.csv", index=False)