import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

df0['gender'] = df0['gender'].map({'M':1, 'F':0}).fillna(0).astype(int)
df0['zip'] = df0['zip'].astype(str).str.extract('(\d+)').astype(int)

df_join_1 = pd.merge(df2, df0, on='user_id', how='inner')
df_join_2 = pd.merge(df_join_1, df1, on='movie_id', how='inner', suffixes=('_x', '_y'))

df_join_2 = df_join_2.astype({
    'movie_id': 'int64',
    'user_id': 'int64',
    'rating': 'int64',
    'timestamp': 'int64',
    'gender': 'int64',
    'age': 'int64',
    'occupation': 'int64',
    'zip': 'int64',
    'title_x': 'int64',
    'genres_x': 'int64',
    'title_y': 'string',
    'genres_y': 'string'
}, errors='ignore')

df_join_2.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)