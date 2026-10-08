import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_2.csv", index_col=0)

agg = df1.groupby(['user_id', 'movie_id']).agg(
    rating=('rating', 'count'),
    timestamp_min=('timestamp', 'min'),
    timestamp_max=('timestamp', 'max')
).reset_index()

merged = pd.merge(agg, df2[['movie_id', 'title']], on='movie_id', how='inner')

final = pd.merge(merged, df0[['user_id', 'age', 'occupation']], on='user_id', how='inner')

final['user_id'] = final['user_id'].astype(float)
final['movie_id'] = final['movie_id'].astype(int)
final['rating'] = final['rating'].astype(float)
final['timestamp'] = ((final['timestamp_min'] + final['timestamp_max']) / 2).astype(float)
final['age'] = final['age'].astype(float)
final['occupation'] = final['occupation'].astype(float)

result = final[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_32/target_multisource_mcts.csv", index=False)