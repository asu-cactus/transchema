import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_2.csv", index_col=0)

grouped = df0.groupby(['user_id', 'movie_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': ['min', 'max']
})
grouped.columns = ['user_id', 'movie_id', 'rating', 'timestamp_min', 'timestamp_max']

grouped['timestamp'] = (grouped['timestamp_min'] + grouped['timestamp_max']) / 2
grouped = grouped.drop(columns=['timestamp_min', 'timestamp_max'])

join1 = pd.merge(grouped, df1, on='user_id', how='inner')
join2 = pd.merge(join1, df2[['movie_id', 'title']], on='movie_id', how='inner')

result = join2[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_27/target_multisource_mcts.csv", index=False)