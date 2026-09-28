import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_2.csv", index_col=0)

df = pd.merge(source2, source1, on="movie_id")
df = pd.merge(df, source0, on="user_id")

df = df[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']]

df['user_id'] = df['user_id'].astype(float)
df['age'] = df['age'].astype(float)
df['occupation'] = df['occupation'].astype(float)
df['movie_id'] = df['movie_id'].astype(int)
df['rating'] = df['rating'].astype(float)
df['timestamp'] = df['timestamp'].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_3/target_multisource_mcts.csv", index=False)