import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_2.csv", index_col=0)

# Join ratings with user info on user_id
joined_1 = pd.merge(df2, df0, on='user_id', how='inner')

# Join the above with movie info on movie_id
final_df = pd.merge(joined_1, df1, on='movie_id', how='inner')

# Map gender to integer
final_df['gender'] = final_df['gender'].map({'M':1, 'F':2}).fillna(0).astype(int)

# Extract numeric part of zip code and convert to int
final_df['zip'] = final_df['zip'].str.extract('(\d+)').astype(float).fillna(0).astype(int)

# Rename columns to match target schema exactly
final_df = final_df.rename(columns={
    'title': 'title_y',
    'genres': 'genres_y'
})

# Add title_x and genres_x as movie_id (integer) as per target schema examples
final_df['title_x'] = final_df['movie_id'].astype(int)
final_df['genres_x'] = final_df['movie_id'].astype(int)

# Select and order columns exactly as target schema
final_df = final_df[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip',
                     'title_x', 'genres_x', 'title_y', 'genres_y']]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_11/target_multisource_mcts.csv", index=False)