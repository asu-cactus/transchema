import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_2.csv", index_col=0)

# Join Source1 (ratings) with Source0 (user info) on user_id
join_01 = pd.merge(source1, source0[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Join the above with Source2 (movie info) on movie_id
join_012 = pd.merge(join_01, source2[['movie_id', 'title']], on='movie_id', how='inner')

# Group by title and movie_id, aggregate mean on other columns
agg_df = join_012.groupby(['title', 'movie_id'], as_index=False).agg({
    'user_id': 'mean',
    'rating': 'mean',
    'timestamp': 'mean',
    'age': 'mean',
    'occupation': 'mean'
})

# Reorder columns to match target schema
result = agg_df[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

# Cast columns to target types
result['title'] = result['title'].astype(str)
result['user_id'] = result['user_id'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_32/target_multisource_mcts.csv", index=False)