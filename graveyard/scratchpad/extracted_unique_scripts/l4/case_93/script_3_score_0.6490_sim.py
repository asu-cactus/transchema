import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

df2_grouped = df2.groupby('movie_id').size().reset_index(name='count')  # implied by GROUP_BY movie_id (not used later but per plan)

df_merged_1 = pd.merge(df2, df0, on='user_id', how='inner')

df_merged = pd.merge(df_merged_1, df1, on='movie_id', how='inner', suffixes=('_x', '_y'))

df_merged['gender'] = df_merged['gender'].map({'M':1, 'F':0}).fillna(0).astype(int)
df_merged['age'] = pd.to_numeric(df_merged['age'], errors='coerce').fillna(0).astype(int)
df_merged['occupation'] = pd.to_numeric(df_merged['occupation'], errors='coerce').fillna(0).astype(int)
df_merged['zip'] = df_merged['zip'].str.extract('(\d+)').fillna('0').astype(int)

df_merged['title_x'] = df_merged['movie_id'].astype(int)
df_merged['genres_x'] = df_merged['movie_id'].astype(int)

df_merged['title_y'] = df_merged['title']
df_merged['genres_y'] = df_merged['genres']

result = df_merged[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip',
                    'title_x', 'genres_x', 'title_y', 'genres_y']]

result = result.astype({
    'movie_id': 'int',
    'user_id': 'int',
    'rating': 'int',
    'timestamp': 'int',
    'gender': 'int',
    'age': 'int',
    'occupation': 'int',
    'zip': 'int',
    'title_x': 'int',
    'genres_x': 'int',
    'title_y': 'string',
    'genres_y': 'string'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)