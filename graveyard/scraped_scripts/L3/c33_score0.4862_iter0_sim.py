import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_2.csv", index_col=0)

grouped = df2.groupby(['user_id', 'movie_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': 'mean'
})

join1 = pd.merge(grouped, df0[['movie_id', 'title']], on='movie_id', how='inner')

join2 = pd.merge(join1, df2[['user_id', 'movie_id']], on=['user_id', 'movie_id'], how='inner')

final = pd.merge(join2, df1[['user_id', 'age', 'occupation']], on='user_id', how='inner')

final = final[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

final['user_id'] = final['user_id'].astype(float)
final['movie_id'] = final['movie_id'].astype(int)
final['rating'] = final['rating'].astype(float)
final['timestamp'] = final['timestamp'].astype(float)
final['age'] = final['age'].astype(float)
final['occupation'] = final['occupation'].astype(float)

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_33/target_multisource_mcts.csv", index=False)