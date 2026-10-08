import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_2.csv", index_col=0)

grouped = df1.groupby(['movie_id', 'user_id'], as_index=False).agg(
    rating=('rating', 'count'),
    timestamp_min=('timestamp', 'min'),
    timestamp_max=('timestamp', 'max')
)

joined_0 = pd.merge(grouped, df0[['movie_id', 'title']], how='inner', on='movie_id')
joined_1 = pd.merge(joined_0, df2[['user_id', 'age', 'occupation']], how='inner', on='user_id')

joined_1 = joined_1.rename(columns={
    'rating': 'rating',
    'timestamp_min': 'timestamp',
    'age': 'age',
    'occupation': 'occupation',
    'title': 'title',
    'user_id': 'user_id',
    'movie_id': 'movie_id'
})

joined_1['user_id'] = joined_1['user_id'].astype(float)
joined_1['movie_id'] = joined_1['movie_id'].astype(int)
joined_1['rating'] = joined_1['rating'].astype(float)
joined_1['timestamp'] = joined_1['timestamp'].astype(float)
joined_1['age'] = joined_1['age'].astype(float)
joined_1['occupation'] = joined_1['occupation'].astype(float)

result = joined_1[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_14/target_multisource_mcts.csv", index=False)