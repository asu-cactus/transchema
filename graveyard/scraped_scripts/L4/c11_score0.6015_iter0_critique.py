import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_0.csv", index_col=0)  # user info
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_1.csv", index_col=0)  # movie info
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_2.csv", index_col=0)  # ratings

# Join ratings with user info on user_id (inner join to keep only matching)
joined_1 = df2.merge(df0, on='user_id', how='inner')

# Join with movie info to get title_x, genres_x
df1_renamed_x = df1.rename(columns={'title': 'title_x', 'genres': 'genres_x'})
joined_2 = joined_1.merge(df1_renamed_x[['movie_id', 'title_x', 'genres_x']], on='movie_id', how='inner')

# Join again with movie info to get title_y, genres_y
df1_renamed_y = df1.rename(columns={'title': 'title_y', 'genres': 'genres_y'})
final = joined_2.merge(df1_renamed_y[['movie_id', 'title_y', 'genres_y']], on='movie_id', how='inner')

# Map gender to integer as per instructions: M=1, F=2, else 0
final['gender'] = final['gender'].map({'M': 1, 'F': 2}).fillna(0).astype(int)

# Convert age, occupation to int, coercing errors to 0
final['age'] = pd.to_numeric(final['age'], errors='coerce').fillna(0).astype(int)
final['occupation'] = pd.to_numeric(final['occupation'], errors='coerce').fillna(0).astype(int)

# Extract numeric part of zip and convert to int
final['zip'] = final['zip'].str.extract('(\d+)').fillna('0').astype(int)

# Ensure rating and timestamp are int
final['rating'] = pd.to_numeric(final['rating'], errors='coerce').fillna(0).astype(int)
final['timestamp'] = pd.to_numeric(final['timestamp'], errors='coerce').fillna(0).astype(int)

# Select and order columns exactly as target schema
final = final[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip',
               'title_x', 'genres_x', 'title_y', 'genres_y']]

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_11/target_multisource_mcts.csv", index=False)