import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_2.csv", index_col=0)

df0['gender'] = df0['gender'].map({'M': 1, 'F': 2}).astype('Int64')
df0['zip'] = df0['zip'].str.extract('(\d+)').astype('Int64')

join_0 = pd.merge(df2, df0, on='user_id', how='inner')
join_1 = pd.merge(join_0, df1, on='movie_id', how='inner')

pivot = join_1.pivot_table(index=['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip'],
                          values=['title', 'genres'], aggfunc='first').reset_index()

pivot.columns = ['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_y', 'genres_y']

pivot['title_x'] = pivot['movie_id'].astype('Int64')
pivot['genres_x'] = pivot['user_id'].astype('Int64')

cols = ['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x', 'title_y', 'genres_y']
pivot = pivot[cols]

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length4_11/target_multisource_mcts.csv", index=False)