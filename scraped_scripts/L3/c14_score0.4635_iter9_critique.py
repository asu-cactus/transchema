import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_0.csv", index_col=0)  # movie info
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_1.csv", index_col=0)  # ratings
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_2.csv", index_col=0)  # user info

# Join ratings with movie titles on movie_id
merged_0 = pd.merge(df1, df0[['movie_id', 'title']], on='movie_id', how='inner')

# Join the above with user info on user_id
merged_1 = pd.merge(merged_0, df2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Group by user_id and movie_id, aggregate mean rating and mean timestamp
agg = merged_1.groupby(['user_id', 'movie_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': 'mean',
    'title': 'first',       # title is same for each movie_id, so take first
    'age': 'first',         # age and occupation are per user_id, take first
    'occupation': 'first'
})

# Reorder columns to match target schema
result = agg[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

# Cast columns to target types
result['title'] = result['title'].astype(str)
result['user_id'] = result['user_id'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_14/target_multisource_mcts.csv", index=False)