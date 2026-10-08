import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

# Map gender to integer codes
df0['gender'] = df0['gender'].map({'M': 1, 'F': 2}).fillna(0).astype(int)

# Extract numeric part of zip code and convert to int
df0['zip'] = df0['zip'].str.extract('(\d+)').fillna('0').astype(int)

# Factorize title and genres in movie table before join to ensure consistent mapping
df1['title_x'] = pd.factorize(df1['title'])[0] + 1
df1['genres_x'] = pd.factorize(df1['genres'])[0] + 1

# Join ratings with user info on user_id
df = df2.merge(df0[['user_id', 'gender', 'age', 'occupation', 'zip']], on='user_id', how='left')

# Join with movie info on movie_id
df = df.merge(df1, on='movie_id', how='left')

# Rename columns to match target schema
df['title_y'] = df['title']
df['genres_y'] = df['genres']

# Select and order columns exactly as target schema
df = df[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip',
         'title_x', 'genres_x', 'title_y', 'genres_y']]

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)