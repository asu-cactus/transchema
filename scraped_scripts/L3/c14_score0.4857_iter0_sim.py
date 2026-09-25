import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_2.csv", index_col=0)

grouped = df1.groupby(['user_id', 'movie_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': 'mean'
})

join1 = pd.merge(grouped, df0[['movie_id', 'title']], on='movie_id', how='inner')

join2 = pd.merge(join1, df2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

join2['user_id'] = join2['user_id'].astype(float)
join2['movie_id'] = join2['movie_id'].astype(int)
join2['rating'] = join2['rating'].astype(float)
join2['timestamp'] = join2['timestamp'].astype(float)
join2['age'] = join2['age'].astype(float)
join2['occupation'] = join2['occupation'].astype(float)

result = join2[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_14/target_multisource_mcts.csv", index=False)