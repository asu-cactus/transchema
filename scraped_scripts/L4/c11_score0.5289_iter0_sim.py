import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_2.csv", index_col=0)

grouped = df2.groupby('movie_id').agg(
    user_id=('user_id', 'first'),
    rating=('rating', 'first'),
    timestamp=('timestamp', 'first')
).reset_index()

grouped = grouped.merge(df1[['movie_id', 'title', 'genres']], left_on='movie_id', right_on='movie_id', how='left')
grouped = grouped.rename(columns={'title': 'title_y', 'genres': 'genres_y'})

joined_1 = grouped.merge(df2, on=['movie_id', 'user_id'], how='inner', suffixes=('_x', '_y'))
joined_1 = joined_1[['movie_id', 'user_id', 'rating_y', 'timestamp_y', 'title_y', 'genres_y']]

joined_2 = joined_1.merge(df0, on='user_id', how='left')

joined_2['gender'] = joined_2['gender'].map({'M': 1, 'F': 2}).fillna(0).astype(int)
joined_2['age'] = pd.to_numeric(joined_2['age'], errors='coerce').fillna(0).astype(int)
joined_2['occupation'] = pd.to_numeric(joined_2['occupation'], errors='coerce').fillna(0).astype(int)
joined_2['zip'] = joined_2['zip'].str.extract('(\d+)').fillna('0').astype(int)

df1_renamed = df1.rename(columns={'title': 'title_x', 'genres': 'genres_x'})
df1_renamed = df1_renamed[['movie_id', 'title_x', 'genres_x']]

final = joined_2.merge(df1_renamed, on='movie_id', how='left')

final = final[['movie_id', 'user_id', 'rating_y', 'timestamp_y', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x', 'title_y', 'genres_y']]
final.columns = ['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x', 'title_y', 'genres_y']

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_11/target_multisource_mcts.csv", index=False)