import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_2.csv", index_col=0)

df1.columns = df1.columns.str.strip()
df1['release date'] = pd.to_datetime(df1['release date'], errors='coerce').dt.year.fillna(0).astype(int)
df1['video release date'] = 0
df1['IMDb URL'] = df1['movie id'].astype(int)
genre_cols = ['unknown', 'Action', 'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance ', 'Sci-Fi', 'Thriller', 'War', 'Western']
for col in genre_cols:
    df1[col] = df1['movie id'].astype(int)

pivot_result = df1.rename(columns={'movie title': 'movie title', 'movie id': 'movie id', 'release date': 'release date', 'video release date': 'video release date'})

join_result_0 = pd.merge(pivot_result, df0, on='user id', how='inner')
final_df = pd.merge(join_result_0, df2, on=['user id', 'movie id'], how='inner')

final_df = final_df[['movie title', 'movie id', 'release date', 'video release date', 'IMDb URL'] + genre_cols + ['user id', 'rating', 'timestamp', 'age', 'gender', 'occupation', 'zip code']]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_96/target_multisource_mcts.csv", index=False)