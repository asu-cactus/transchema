import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

# Map gender to integer
df0['gender'] = df0['gender'].map({'M':1, 'F':0}).fillna(0).astype(int)

# Extract numeric part of zip and convert to int
df0['zip'] = df0['zip'].astype(str).str.extract('(\d+)').astype(int)

# Join ratings with user info on user_id
df_join_1 = pd.merge(df2, df0, on='user_id', how='inner')

# Join the above with movie info on movie_id
df_join_2 = pd.merge(df_join_1, df1, on='movie_id', how='inner')

# Rename columns to match target schema exactly
# Target schema: ['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x', 'title_y', 'genres_y']
# From sources:
# - title and genres from df1 (movie info) should be split into title_y and genres_y (strings)
# - title_x and genres_x are integers in target but source has no such columns; likely these are placeholders or zero-filled columns
# Since title_x and genres_x are integers and no source columns correspond, fill with 0

df_join_2 = df_join_2.rename(columns={
    'title': 'title_y',
    'genres': 'genres_y'
})

# Add title_x and genres_x as integer columns filled with 0 to match target schema
df_join_2['title_x'] = 0
df_join_2['genres_x'] = 0

# Select and reorder columns exactly as target schema
df_final = df_join_2[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip',
                      'title_x', 'genres_x', 'title_y', 'genres_y']]

# Group by movie_id and user_id to remove duplicates (no aggregation needed)
df_final = df_final.drop_duplicates(subset=['movie_id', 'user_id'])

# Ensure correct dtypes
df_final = df_final.astype({
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
})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)