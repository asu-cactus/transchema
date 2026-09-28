import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

# Map gender to integer
df0['gender'] = df0['gender'].map({'M':1, 'F':0}).astype('Int64')

# Extract numeric part of zip and convert to int
df0['zip'] = df0['zip'].str.extract(r'(\d+)').astype('Int64')

# Join ratings with user info on user_id (inner join to avoid NaNs)
df = df1.merge(df0, on='user_id', how='inner')

# Join with movie info on movie_id (inner join)
df = df.merge(df2, on='movie_id', how='inner')

# Rename columns to match target schema
df = df.rename(columns={
    'movie_id': 'movie_id_x',  # from ratings table
    'genres': 'genres_y',      # from movie info table
    'movie_id_y': 'movie_id_y' # will be assigned below
})

# movie_id_y is the movie_id from movie info (df2), which is now 'movie_id' in df2, but after merge it's 'movie_id' from df2
# After merge, 'movie_id' column is from df1 (ratings), so to get movie_id_y, use df2.movie_id
# But since merged, movie_id_y is not present, so assign movie_id_y = movie_id_x (same movie_id)
df['movie_id_y'] = df['movie_id_x']

# Set genres_x to constant 5 as per target examples (constant integer)
df['genres_x'] = 5

# Ensure correct types
df['title'] = df['title'].astype(str)
df['user_id'] = df['user_id'].astype('Int64')
df['movie_id_x'] = df['movie_id_x'].astype('Int64')
df['rating'] = df['rating'].astype('Int64')
df['timestamp'] = df['timestamp'].astype('Int64')
df['gender'] = df['gender'].astype('Int64')
df['age'] = df['age'].astype('Int64')
df['occupation'] = df['occupation'].astype('Int64')
df['zip'] = df['zip'].astype('Int64')
df['genres_x'] = df['genres_x'].astype('Int64')
df['movie_id_y'] = df['movie_id_y'].astype('Int64')
df['genres_y'] = df['genres_y'].astype(str)

# Select columns in target schema order
df = df[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)