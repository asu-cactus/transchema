import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_2.csv", index_col=0)

grouped = df2.groupby('movie_id').agg(
    user_id_mean=('user_id', 'mean'),
    rating_mean=('rating', 'mean'),
    timestamp_mean=('timestamp', 'mean')
).reset_index()

grouped = grouped.rename(columns={
    'user_id_mean': 'user_id',
    'rating_mean': 'rating',
    'timestamp_mean': 'timestamp'
})

join1 = pd.merge(grouped, df1[['movie_id', 'title']], on='movie_id', how='inner')

join2 = pd.merge(join1, df2[['user_id', 'movie_id']], on=['user_id', 'movie_id'], how='inner')

final = pd.merge(join2, df0[['user_id', 'age', 'occupation']], on='user_id', how='inner')

final = final[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_3/target_multisource_mcts.csv", index=False)