import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_2.csv", index_col=0)

union_result = pd.concat([source1, source2], axis=1, join='inner')

df = union_result.merge(source0[['movie_id', 'title']], on='movie_id', how='inner')

df = df[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

df['user_id'] = df['user_id'].astype(float)
df['movie_id'] = df['movie_id'].astype(int)
df['rating'] = df['rating'].astype(float)
df['timestamp'] = df['timestamp'].astype(float)
df['age'] = df['age'].astype(float)
df['occupation'] = df['occupation'].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_33/target_multisource_mcts.csv", index=False)