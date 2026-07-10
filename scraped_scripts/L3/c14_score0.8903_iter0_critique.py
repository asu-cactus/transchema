import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_2.csv", index_col=0)

# Join ratings with movies on movie_id
join1 = pd.merge(df1, df0[['movie_id', 'title']], on='movie_id', how='inner')

# Join the above with user demographics on user_id
join2 = pd.merge(join1, df2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Group by title and aggregate other columns by mean
result = join2.groupby('title', as_index=False).agg({
    'user_id': 'mean',
    'movie_id': 'mean',
    'rating': 'mean',
    'timestamp': 'mean',
    'age': 'mean',
    'occupation': 'mean'
})

# Cast columns to match target schema types
result['user_id'] = result['user_id'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)

result = result[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_14/target_multisource_mcts.csv", index=False)