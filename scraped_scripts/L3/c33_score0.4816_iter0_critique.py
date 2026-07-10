import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_2.csv", index_col=0)

# Join ratings with movies to get title
join1 = pd.merge(df2, df0[['movie_id', 'title']], on='movie_id', how='inner')

# Join with users to get age and occupation
join2 = pd.merge(join1, df1[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Group by title, user_id, movie_id and aggregate other columns by mean
grouped = join2.groupby(['title', 'user_id', 'movie_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': 'mean',
    'age': 'mean',
    'occupation': 'mean'
})

# Cast columns to target types
grouped['user_id'] = grouped['user_id'].astype(float)
grouped['movie_id'] = grouped['movie_id'].astype(int)
grouped['rating'] = grouped['rating'].astype(float)
grouped['timestamp'] = grouped['timestamp'].astype(float)
grouped['age'] = grouped['age'].astype(float)
grouped['occupation'] = grouped['occupation'].astype(float)

# Reorder columns as per target schema
final = grouped[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_33/target_multisource_mcts.csv", index=False)