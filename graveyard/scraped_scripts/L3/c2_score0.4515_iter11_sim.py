import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_2.csv", index_col=0)

agg = df0.groupby('movie_id').agg(
    movie_id_count=('movie_id', 'count'),
    rating_avg=('rating', 'mean')
).reset_index()

occupation_avg = df2.groupby('user_id').agg(
    occupation_avg=('occupation', 'mean'),
    age_avg=('age', 'mean')
).reset_index()

df0_1 = pd.merge(df0, df1[['movie_id', 'title']], on='movie_id', how='inner')
df0_1_2 = pd.merge(df0_1, df2, on='user_id', how='inner')

result = df0_1_2[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_2/target_multisource_mcts.csv", index=False)