import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_2.csv", index_col=0)

agg = s1.groupby(['user_id', 'movie_id'], as_index=False).agg({'rating':'mean', 'timestamp':'mean'})

join_0 = pd.merge(s0, agg, on='user_id', how='inner')
join_1 = pd.merge(s2[['movie_id', 'title']], join_0, on='movie_id', how='inner')

result = join_1.rename(columns={
    'rating': 'rating',
    'timestamp': 'timestamp',
    'age': 'age',
    'occupation': 'occupation',
    'title': 'title',
    'user_id': 'user_id',
    'movie_id': 'movie_id'
})[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_32/target_multisource_mcts.csv", index=False)