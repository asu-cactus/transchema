import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

agg = df1.groupby(['movie_id', 'user_id']).agg(
    rating=('rating', 'mean'),
    unix_timestamp_min=('unix_timestamp', 'min'),
    unix_timestamp_max=('unix_timestamp', 'max')
).reset_index()

agg['unix_timestamp'] = (agg['unix_timestamp_min'] + agg['unix_timestamp_max']) / 2
agg = agg.drop(columns=['unix_timestamp_min', 'unix_timestamp_max'])

merged_0 = pd.merge(agg, df0[['movie_id', 'title', 'video_release_date']], on='movie_id', how='inner')
merged = pd.merge(merged_0, df2[['user_id', 'age']], on='user_id', how='inner')

result = merged[['title', 'movie_id', 'video_release_date', 'user_id', 'rating', 'unix_timestamp', 'age']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)