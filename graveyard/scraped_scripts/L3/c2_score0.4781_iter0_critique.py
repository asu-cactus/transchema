import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_2.csv", index_col=0)

# Join ratings with movies on movie_id
join1 = pd.merge(df0, df1[['movie_id', 'title']], on='movie_id', how='inner')

# Join the above with user info on user_id
join2 = pd.merge(join1, df2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Group by title, user_id, movie_id and aggregate other columns by mean
grouped = join2.groupby(['title', 'user_id', 'movie_id'], as_index=False).agg({
    'age': 'mean',
    'occupation': 'mean',
    'rating': 'mean',
    'timestamp': 'mean'
})

# Reorder columns to match target schema
result = grouped[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']]

# Cast columns to correct types
result['user_id'] = result['user_id'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_2/target_multisource_mcts.csv", index=False)