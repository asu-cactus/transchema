import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_2.csv", index_col=0)

agg = df0.groupby('movie_id').agg(
    user_id_avg=('user_id', 'mean'),
    rating_avg=('rating', 'mean'),
    movie_id_count=('movie_id', 'count'),
    timestamp_avg=('timestamp', 'mean')
).reset_index()

merged = pd.merge(agg, df2, on='movie_id', how='inner')

merged = merged.rename(columns={'user_id_avg': 'user_id', 'rating_avg': 'rating', 'timestamp_avg': 'timestamp'})

final = pd.merge(merged, df1, on='user_id', how='inner')

final = final[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_27/target_multisource_mcts.csv", index=False)