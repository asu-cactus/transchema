import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_2.csv", index_col=0)

grouped = df0.groupby(['user_id', 'movie_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': 'mean'
})

join1 = pd.merge(grouped, df0, on=['user_id', 'movie_id'], how='inner', suffixes=('_agg', ''))
join1 = join1.drop(columns=['rating', 'timestamp'])
join1 = join1.rename(columns={'rating_agg': 'rating', 'timestamp_agg': 'timestamp'})

join2 = pd.merge(join1, df1[['user_id', 'age', 'occupation']], on='user_id', how='inner')

join3 = pd.merge(join2, df2[['movie_id', 'title']], on='movie_id', how='inner')

result = join3[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result['user_id'] = result['user_id'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_27/target_multisource_mcts.csv", index=False)