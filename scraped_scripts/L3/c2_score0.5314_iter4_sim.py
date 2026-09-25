import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_2.csv", index_col=0)

union_result = pd.concat([source0, source2], ignore_index=True, sort=False)

joined = union_result.merge(source1[['movie_id', 'title']], on='movie_id', how='inner')

grouped = joined.groupby('title').agg({
    'user_id': 'mean',
    'age': 'mean',
    'occupation': 'mean',
    'movie_id': 'first',
    'rating': 'mean',
    'timestamp': 'mean'
}).reset_index()

grouped['user_id'] = grouped['user_id'].astype(float)
grouped['age'] = grouped['age'].astype(float)
grouped['occupation'] = grouped['occupation'].astype(float)
grouped['movie_id'] = grouped['movie_id'].astype(int)
grouped['rating'] = grouped['rating'].astype(float)
grouped['timestamp'] = grouped['timestamp'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_2/target_multisource_mcts.csv", index=False)