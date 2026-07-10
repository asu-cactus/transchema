import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv"
src2_path = "autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)
df2 = pd.read_csv(src2_path, index_col=0)

df0['gender'] = df0['gender'].map({'M':1, 'F':0}).astype('Int64')
df0['zip'] = df0['zip'].str.extract('(\d+)').astype('Int64')

joined_1 = pd.merge(df1, df2, how='inner', left_on='movie_id', right_on='movie_id', suffixes=('_x', '_y'))
joined_2 = pd.merge(joined_1, df0, how='inner', left_on='user_id', right_on='user_id')

result = joined_2.rename(columns={
    'title': 'title',
    'user_id': 'user_id',
    'movie_id_x': 'movie_id_x',
    'rating': 'rating',
    'timestamp': 'timestamp',
    'gender': 'gender',
    'age': 'age',
    'occupation': 'occupation',
    'zip': 'zip',
    'movie_id_x': 'movie_id_x',
    'genres_x': 'genres_x',
    'movie_id_y': 'movie_id_y',
    'genres_y': 'genres_y'
})

result = result[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'movie_id_x', 'genres_x', 'movie_id_y', 'genres_y']]

result['genres_x'] = result['genres_x'].astype('Int64', errors='ignore')
result['genres_y'] = result['genres_y'].astype(str)

result.to_csv(target_path, index=False)