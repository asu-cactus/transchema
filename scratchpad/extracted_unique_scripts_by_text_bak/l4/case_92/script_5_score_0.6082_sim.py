import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

df0['gender'] = df0['gender'].map({'M':1, 'F':2}).fillna(0).astype(int)
df0['zip'] = df0['zip'].str.extract('(\d+)').astype(int)

df2_renamed = df2.rename(columns={'movie_id': 'movie_id_y', 'genres': 'genres_y'})

df1_renamed = df1.rename(columns={'movie_id': 'movie_id_x'})

merged_1 = pd.merge(df1_renamed, df0, on='user_id', how='inner')

merged_2 = pd.merge(merged_1, df2_renamed, left_on='movie_id_x', right_on='movie_id_y', how='inner')

result = merged_2[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'movie_id_y', 'genres_y']]

result['genres_x'] = 1

result = result[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)