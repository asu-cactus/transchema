import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_2.csv", index_col=0)

df0['movie_id'] = df0['movie_id'].astype(float)
df0['timestamp'] = df0['timestamp'].astype(float)

merged_0_1 = pd.merge(df0, df1, on='movie_id', how='inner')
merged_all = pd.merge(merged_0_1, df2, on='user_id', how='inner')

grouped = merged_all.groupby('title').agg(
    user_id=('user_id', 'count'),
    age=('age', 'mean'),
    occupation=('occupation', 'mean'),
    movie_id=('movie_id', 'mean'),
    rating=('rating', 'mean'),
    timestamp=('timestamp', 'mean')
).reset_index()

grouped['user_id'] = grouped['user_id'].astype(float)
grouped['age'] = grouped['age'].astype(float)
grouped['occupation'] = grouped['occupation'].astype(float)
grouped['movie_id'] = grouped['movie_id'].astype(int)
grouped['rating'] = grouped['rating'].astype(float)
grouped['timestamp'] = grouped['timestamp'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_2/target_multisource_mcts.csv", index=False)