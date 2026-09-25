import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_2.csv", index_col=0)

groupby_result = df2.groupby('movie_id', as_index=False).size().rename(columns={'size': 'count'})

joined_1 = pd.merge(groupby_result, df1, on='movie_id', how='inner')

joined_2 = pd.merge(joined_1, df2, on='movie_id', how='inner')

final_df = pd.merge(joined_2, df0, on='user_id', how='inner')

final_df['gender'] = final_df['gender'].map({'M':1, 'F':2}).fillna(0).astype(int)
final_df['zip'] = final_df['zip'].str.extract('(\d+)').astype(float).fillna(0).astype(int)

final_df = final_df.rename(columns={
    'title_x': 'title_x',
    'genres_x': 'genres_x',
    'title': 'title_y',
    'genres': 'genres_y'
})

final_df['title_x'] = final_df['movie_id'].astype(int)
final_df['genres_x'] = final_df['movie_id'].astype(int)

final_df = final_df[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip',
                     'title_x', 'genres_x', 'title_y', 'genres_y']]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_11/target_multisource_mcts.csv", index=False)