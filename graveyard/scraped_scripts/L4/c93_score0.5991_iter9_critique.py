import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

# Join ratings with user info on user_id
df = pd.merge(df2, df0, on='user_id')

# Join with movie info on movie_id
df = pd.merge(df, df1, on='movie_id')

# Map gender to integer
df['gender'] = df['gender'].map({'M': 1, 'F': 0}).astype('Int64')

# Convert age, occupation to integer
df['age'] = pd.to_numeric(df['age'], errors='coerce').astype('Int64')
df['occupation'] = pd.to_numeric(df['occupation'], errors='coerce').astype('Int64')

# Extract numeric part of zip and convert to integer
df['zip'] = df['zip'].str.extract('(\d+)').astype('Int64')

# Rename movie columns to match target schema
df = df.rename(columns={'title': 'title_y', 'genres': 'genres_y'})

# Set title_x and genres_x equal to rating to match integer columns in target schema
df['title_x'] = df['rating']
df['genres_x'] = df['rating']

# Group by movie_id and user_id to remove duplicates and aggregate other columns by first
df = df.groupby(['movie_id', 'user_id'], as_index=False).agg({
    'rating': 'first',
    'timestamp': 'first',
    'gender': 'first',
    'age': 'first',
    'occupation': 'first',
    'zip': 'first',
    'title_x': 'first',
    'genres_x': 'first',
    'title_y': 'first',
    'genres_y': 'first'
})

# Reorder columns to match target schema
df = df[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x', 'title_y', 'genres_y']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)