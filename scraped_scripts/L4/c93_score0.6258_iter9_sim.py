import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

df2_unpivot = df2.melt(id_vars=['user_id', 'movie_id'], value_vars=['rating', 'timestamp'], var_name='variable', value_name='value')
df_rating = df2_unpivot[df2_unpivot['variable'] == 'rating'].drop(columns=['variable']).rename(columns={'value': 'rating'})
df_timestamp = df2_unpivot[df2_unpivot['variable'] == 'timestamp'].drop(columns=['variable']).rename(columns={'value': 'timestamp'})
df = pd.merge(df_rating, df_timestamp, on=['user_id', 'movie_id'])

df = pd.merge(df, df0, on='user_id')
df = pd.merge(df, df1, on='movie_id')

df['gender'] = df['gender'].map({'M':1, 'F':0}).astype('Int64')
df['age'] = pd.to_numeric(df['age'], errors='coerce').astype('Int64')
df['occupation'] = pd.to_numeric(df['occupation'], errors='coerce').astype('Int64')
df['zip'] = df['zip'].str.extract('(\d+)').astype('Int64')

df['title_x'] = df.groupby('movie_id').cumcount() + 1
df['genres_x'] = df['title_x']

df = df.rename(columns={'title': 'title_y', 'genres': 'genres_y'})

df = df[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x', 'title_y', 'genres_y']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)