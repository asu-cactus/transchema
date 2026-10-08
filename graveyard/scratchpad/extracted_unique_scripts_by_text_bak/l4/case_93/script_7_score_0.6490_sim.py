import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

df_merged_0 = pd.merge(df2, df0, on="user_id", how="inner")
df_merged = pd.merge(df_merged_0, df1, on="movie_id", how="inner")

df_merged['gender'] = df_merged['gender'].map({'M': 1, 'F': 2}).astype('Int64')

df_merged['title_x'] = df_merged['title'].astype('category').cat.codes
df_merged['genres_x'] = df_merged['genres'].astype('category').cat.codes

result = df_merged[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x', 'title', 'genres']]

result = result.rename(columns={'title': 'title_y', 'genres': 'genres_y'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)