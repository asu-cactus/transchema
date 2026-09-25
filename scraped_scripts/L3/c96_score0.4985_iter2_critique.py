import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_96/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_96/training_1.csv"
source2_path = "autopipeline-benchmarks/github-pipelines/length3_96/training_2.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length3_96/target_multisource_mcts.csv"

# Read sources with index_col=0 to ignore the first index column
df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)
df2 = pd.read_csv(source2_path, index_col=0)

genre_cols = ['unknown', 'Action', 'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime',
              'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery',
              'Romance ', 'Sci-Fi', 'Thriller', 'War', 'Western']

# Join Source1 and Source2 on 'movie id'
df_join_1 = pd.merge(df1, df2, on='movie id', how='inner')

# Join the above with Source0 on 'user id'
df_join_all = pd.merge(df_join_1, df0, on='user id', how='inner')

# Convert 'release date', 'video release date', 'IMDb URL' to categorical codes (integers)
df_join_all['release date'] = df_join_all['release date'].astype('category').cat.codes.astype('Int64')
df_join_all['video release date'] = df_join_all['video release date'].astype('category').cat.codes.astype('Int64')
df_join_all['IMDb URL'] = df_join_all['IMDb URL'].astype('category').cat.codes.astype('Int64')

# Convert genre columns to integer type (fill missing with 0)
for col in genre_cols:
    df_join_all[col] = pd.to_numeric(df_join_all[col], errors='coerce').fillna(0).astype('Int64')

# Convert 'gender', 'occupation', 'zip code' to categorical codes (integers)
df_join_all['gender'] = df_join_all['gender'].astype('category').cat.codes.astype('Int64')
df_join_all['occupation'] = df_join_all['occupation'].astype('category').cat.codes.astype('Int64')
df_join_all['zip code'] = df_join_all['zip code'].astype('category').cat.codes.astype('Int64')

# Convert other integer columns to Int64
df_join_all['movie id'] = pd.to_numeric(df_join_all['movie id'], errors='coerce').astype('Int64')
df_join_all['user id'] = pd.to_numeric(df_join_all['user id'], errors='coerce').astype('Int64')
df_join_all['rating'] = pd.to_numeric(df_join_all['rating'], errors='coerce').astype('Int64')
df_join_all['timestamp'] = pd.to_numeric(df_join_all['timestamp'], errors='coerce').astype('Int64')
df_join_all['age'] = pd.to_numeric(df_join_all['age'], errors='coerce').astype('Int64')

# Select columns in exact target schema order
final_cols = ['movie title', 'movie id', 'release date', 'video release date', 'IMDb URL'] + genre_cols + \
             ['user id', 'rating', 'timestamp', 'age', 'gender', 'occupation', 'zip code']

df_final = df_join_all[final_cols]

df_final.to_csv(target_path, index=False)