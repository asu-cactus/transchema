import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_2.csv", index_col=0)

grouped = df1.groupby(['user_id', 'movie_id']).agg(
    rating=('rating', 'count'),
    timestamp_min=('timestamp', 'min'),
    timestamp_max=('timestamp', 'max')
).reset_index()

joined_0 = pd.merge(grouped, df0[['movie_id', 'title']], on='movie_id', how='inner')

joined_1 = pd.merge(joined_0, df2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

joined_1['user_id'] = joined_1['user_id'].astype(float)
joined_1['movie_id'] = joined_1['movie_id'].astype(int)
joined_1['rating'] = joined_1['rating'].astype(float)
joined_1['timestamp'] = (joined_1['timestamp_min'] + joined_1['timestamp_max']) / 2
joined_1['timestamp'] = joined_1['timestamp'].astype(float)
joined_1['age'] = joined_1['age'].astype(float)
joined_1['occupation'] = joined_1['occupation'].astype(float)

result = joined_1[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_19/target_multisource_mcts.csv", index=False)