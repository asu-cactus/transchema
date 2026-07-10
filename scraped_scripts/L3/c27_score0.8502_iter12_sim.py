import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_2.csv", index_col=0)

agg = df0.groupby('movie_id').agg(
    user_id_count=('user_id', 'count'),
    rating_avg=('rating', 'mean'),
    timestamp_avg=('timestamp', 'mean')
).reset_index()

age_occ = df1.groupby('user_id').agg(
    age_avg=('age', 'mean'),
    occupation_avg=('occupation', 'mean')
).reset_index()

join_1 = pd.merge(df0, age_occ, on='user_id', how='inner')

join_2 = pd.merge(join_1, df2, on='movie_id', how='inner')

grouped = join_2.groupby('title').agg(
    user_id=('user_id', 'count'),
    movie_id=('movie_id', 'first'),
    rating=('rating', 'mean'),
    timestamp=('timestamp', 'mean'),
    age=('age_avg', 'mean'),
    occupation=('occupation_avg', 'mean')
).reset_index()

grouped['user_id'] = grouped['user_id'].astype(float)
grouped['movie_id'] = grouped['movie_id'].astype(int)
grouped['rating'] = grouped['rating'].astype(float)
grouped['timestamp'] = grouped['timestamp'].astype(float)
grouped['age'] = grouped['age'].astype(float)
grouped['occupation'] = grouped['occupation'].astype(float)

grouped = grouped[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_27/target_multisource_mcts.csv", index=False)