import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_0.csv", index_col=0)  # users
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_1.csv", index_col=0)  # ratings
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_2.csv", index_col=0)  # movies

# Join ratings with movies on movie_id to get title
df1_2 = pd.merge(df1, df2[['movie_id', 'title']], on='movie_id', how='inner')

# Join the above with users on user_id to get demographics
df_all = pd.merge(df1_2, df0[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Group by title and aggregate other columns by mean
result = df_all.groupby('title', as_index=False).agg({
    'user_id': 'mean',
    'movie_id': 'mean',
    'rating': 'mean',
    'timestamp': 'mean',
    'age': 'mean',
    'occupation': 'mean'
})

# Cast columns to target types
result['user_id'] = result['user_id'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_25/target_multisource_mcts.csv", index=False)