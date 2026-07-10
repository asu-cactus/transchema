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

# Select columns exactly as in target schema
result = joined_2[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

# Ensure correct dtypes
result['gender'] = result['gender'].astype('Int64')
result['zip'] = result['zip'].astype('Int64')
result['user_id'] = result['user_id'].astype('Int64')
result['movie_id_x'] = result['movie_id_x'].astype('Int64')
result['rating'] = result['rating'].astype('Int64')
result['timestamp'] = result['timestamp'].astype('Int64')
result['age'] = result['age'].astype('Int64')
result['occupation'] = result['occupation'].astype('Int64')
result['movie_id_y'] = result['movie_id_y'].astype('Int64')

# genres_x and genres_y remain as string (genres_x is string from source2)
result['genres_x'] = result['genres_x'].astype(str)
result['genres_y'] = result['genres_y'].astype(str)

result.to_csv(target_path, index=False)