import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_2.csv", index_col=0)

grouped = df1.groupby(['user_id', 'movie_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': 'mean'
})

merged1 = pd.merge(grouped, df1[['user_id', 'movie_id']], on=['user_id', 'movie_id'], how='inner')
merged2 = pd.merge(merged1, df2[['movie_id', 'title']], on='movie_id', how='inner')
merged3 = pd.merge(merged2, df0[['user_id', 'age', 'occupation']], on='user_id', how='inner')

result = merged3[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result['user_id'] = result['user_id'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_25/target_multisource_mcts.csv", index=False)