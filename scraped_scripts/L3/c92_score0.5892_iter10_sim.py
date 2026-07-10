import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)

agg = df2.groupby('movie_id').agg(
    user_count=('user_id', 'count'),
    rating_min=('rating', 'min'),
    rating_max=('rating', 'max'),
    user_id_mean=('user_id', 'mean'),
    rating_mean=('rating', 'mean'),
    unix_timestamp_mean=('unix_timestamp', 'mean')
).reset_index()

joined_0 = pd.merge(df0, agg, how='inner', left_on='movie_id', right_on='movie_id')

joined_1 = pd.merge(joined_0, df1, how='inner', left_on='user_id_mean', right_on='user_id')

result = pd.DataFrame()
result['title'] = joined_1['title']
result['movie_id'] = joined_1['movie_id']
result['video_release_date'] = pd.to_numeric(joined_1['video_release_date'], errors='coerce')
result['user_id'] = joined_1['user_id_mean']
result['rating'] = joined_1['rating_mean']
result['unix_timestamp'] = joined_1['unix_timestamp_mean']
result['age'] = joined_1['age'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)