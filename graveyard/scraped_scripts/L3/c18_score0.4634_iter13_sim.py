import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_2.csv", index_col=0)

agg = df2.groupby(['user_id', 'movie_id']).agg(
    rating=('rating', 'mean'),
    timestamp=('timestamp', 'mean')
).reset_index()

user_agg = df0.groupby('user_id').agg(
    age=('age', 'mean'),
    occupation=('occupation', 'mean')
).reset_index()

agg = agg.merge(user_agg, on='user_id', how='inner')

result = agg.merge(df1[['movie_id', 'title']], on='movie_id', how='inner')

result = result[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_18/target_multisource_mcts.csv", index=False)