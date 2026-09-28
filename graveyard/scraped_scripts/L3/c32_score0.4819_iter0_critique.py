import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_2.csv", index_col=0)

# Join Source1 and Source2 on movie_id
joined_1 = pd.merge(df1, df2[['movie_id', 'title']], on='movie_id', how='inner')

# Join the above with Source0 on user_id
joined_2 = pd.merge(joined_1, df0[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Group by title, user_id, movie_id and aggregate numeric columns by mean
final = joined_2.groupby(['title', 'user_id', 'movie_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': 'mean',
    'age': 'mean',
    'occupation': 'mean'
})

# Cast columns to match target schema types
final['user_id'] = final['user_id'].astype(float)
final['movie_id'] = final['movie_id'].astype(int)
final['rating'] = final['rating'].astype(float)
final['timestamp'] = final['timestamp'].astype(float)
final['age'] = final['age'].astype(float)
final['occupation'] = final['occupation'].astype(float)

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_32/target_multisource_mcts.csv", index=False)