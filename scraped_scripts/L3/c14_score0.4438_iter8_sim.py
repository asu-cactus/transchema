import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_2.csv", index_col=0)

genres_expanded = source0.assign(genres=source0['genres'].str.split('|')).explode('genres').rename(columns={'genres': 'genre'})

join_1 = pd.merge(genres_expanded, source1, on='movie_id', how='inner')

join_2 = pd.merge(join_1, source2.drop(columns=['gender', 'zip']), on='user_id', how='inner')

result = join_2[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result['title'] = result['title'].astype(str)
result['user_id'] = result['user_id'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_14/target_multisource_mcts.csv", index=False)