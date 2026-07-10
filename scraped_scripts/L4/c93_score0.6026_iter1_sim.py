import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

pivot_title = df1.pivot(index='movie_id', columns='title', values='movie_id')
pivot_genres = df1.pivot(index='movie_id', columns='genres', values='movie_id')

pivot_title.columns = [f"title_{i}" for i in range(len(pivot_title.columns))]
pivot_genres.columns = [f"genres_{i}" for i in range(len(pivot_genres.columns))]

pivot_result = pd.concat([pivot_title, pivot_genres], axis=1).reset_index()

join_result_1 = pd.merge(pivot_result, df2, on='movie_id', how='inner')
join_result_2 = pd.merge(join_result_1, df0, on='user_id', how='inner')

join_result_2['gender'] = join_result_2['gender'].map({'M':1, 'F':0}).fillna(0).astype(int)
join_result_2['age'] = pd.to_numeric(join_result_2['age'], errors='coerce').fillna(0).astype(int)
join_result_2['occupation'] = pd.to_numeric(join_result_2['occupation'], errors='coerce').fillna(0).astype(int)
join_result_2['zip'] = join_result_2['zip'].str.extract('(\d+)').fillna('0').astype(int)

title_x_cols = [c for c in join_result_2.columns if c.startswith('title_')]
genres_x_cols = [c for c in join_result_2.columns if c.startswith('genres_')]

join_result_2['title_x'] = join_result_2[title_x_cols].notna().astype(int).sum(axis=1)
join_result_2['genres_x'] = join_result_2[genres_x_cols].notna().astype(int).sum(axis=1)

title_y = df1.set_index('movie_id')['title']
genres_y = df1.set_index('movie_id')['genres']

join_result_2['title_y'] = join_result_2['movie_id'].map(title_y)
join_result_2['genres_y'] = join_result_2['movie_id'].map(genres_y)

final_cols = ['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x', 'title_y', 'genres_y']
final_df = join_result_2[final_cols]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)