import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_2.csv", index_col=0)

# Join Source0 and Source1 on movie_id
join_0 = pd.merge(source0, source1[['movie_id', 'title']], on='movie_id', how='inner')

# Join the above result with Source2 on user_id
join_1 = pd.merge(join_0, source2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Group by title and movie_id, aggregate other columns by mean
agg_df = join_1.groupby(['title', 'movie_id'], as_index=False).agg({
    'user_id': 'mean',
    'age': 'mean',
    'occupation': 'mean',
    'rating': 'mean',
    'timestamp': 'mean'
})

# Reorder columns to match target schema
result = agg_df[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']].copy()

# Cast columns to correct types
result['user_id'] = result['user_id'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_2/target_multisource_mcts.csv", index=False)