import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_2.csv", index_col=0)

join_01 = pd.merge(df0, df1, on='movie_id', how='inner')
join_012 = pd.merge(join_01, df2, on='user_id', how='inner')

grouped = join_012.groupby(['title', 'movie_id', 'timestamp'], as_index=False).agg({
    'user_id': 'mean',
    'rating': 'mean',
    'age': 'mean',
    'occupation': 'mean'
})

result = grouped[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_19/target_multisource_mcts.csv", index=False)