import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_2.csv", index_col=0)

pivot = df0.pivot_table(index='user_id', values=['age', 'gender', 'occupation', 'zip'], aggfunc='first').reset_index()

grouped = df1.groupby('movie_id', as_index=False).agg({
    'user_id': 'first',
    'rating': 'first',
    'timestamp': 'first'
})

join1 = pd.merge(grouped, pivot, on='user_id', how='inner')

join2 = pd.merge(join1, df2, on='movie_id', how='inner')

join2['movie_title_x'] = join2['movie_title'].astype('category').cat.codes
join2['year_x'] = pd.to_numeric(join2['year'], errors='coerce').fillna(0).astype(int)
join2['movie_title_y'] = join2['movie_title']
join2['year_y'] = join2['year'].astype(str)

result = join2[['movie_id', 'movie_title_x', 'year_x', 'user_id', 'rating', 'timestamp', 'age', 'gender', 'occupation', 'zip', 'movie_title_y', 'year_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_10/target_multisource_mcts.csv", index=False)