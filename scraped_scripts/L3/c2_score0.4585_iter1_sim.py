import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_2.csv", index_col=0)

join_0 = pd.merge(source0, source1[['movie_id', 'title']], on='movie_id', how='inner')
join_1 = pd.merge(join_0, source2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

result = join_1[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']].copy()

result['user_id'] = result['user_id'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_2/target_multisource_mcts.csv", index=False)