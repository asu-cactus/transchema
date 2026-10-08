import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_2.csv", index_col=0)

# Join Source2 (ratings) with Source1 (movies) on movie_id
df_join_1 = pd.merge(df2, df1, on='movie_id', how='inner')

# Encode title_x and genres_x as integer codes from title and genres
df_join_1['title_x'] = df_join_1['title'].astype('category').cat.codes + 1
df_join_1['genres_x'] = df_join_1['genres'].astype('category').cat.codes + 1

# Rename title and genres to title_y and genres_y to match target schema
df_join_1 = df_join_1.rename(columns={'title': 'title_y', 'genres': 'genres_y'})

# Join the above with Source0 (users) on user_id
df_join_2 = pd.merge(df_join_1, df0, on='user_id', how='inner')

# Convert gender to integer: map 'M'->1, 'F'->2, else NaN
df_join_2['gender'] = df_join_2['gender'].map({'M': 1, 'F': 2})

# Convert age, occupation, zip to integers where possible
df_join_2['age'] = pd.to_numeric(df_join_2['age'], errors='coerce').astype('Int64')
df_join_2['occupation'] = pd.to_numeric(df_join_2['occupation'], errors='coerce').astype('Int64')

# For zip, remove non-digit characters and convert to int if possible
df_join_2['zip'] = df_join_2['zip'].astype(str).str.extract('(\d+)')
df_join_2['zip'] = pd.to_numeric(df_join_2['zip'], errors='coerce').astype('Int64')

# Ensure rating and timestamp are integers
df_join_2['rating'] = pd.to_numeric(df_join_2['rating'], errors='coerce').astype('Int64')
df_join_2['timestamp'] = pd.to_numeric(df_join_2['timestamp'], errors='coerce').astype('Int64')

# Ensure movie_id and user_id are integers
df_join_2['movie_id'] = pd.to_numeric(df_join_2['movie_id'], errors='coerce').astype('Int64')
df_join_2['user_id'] = pd.to_numeric(df_join_2['user_id'], errors='coerce').astype('Int64')

# Group by movie_id and user_id to remove duplicates and ensure uniqueness
# For aggregation, take first non-null value for each column
agg_dict = {
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
}

result = df_join_2.groupby(['movie_id', 'user_id'], as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
result = result[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip',
                 'title_x', 'genres_x', 'title_y', 'genres_y']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_11/target_multisource_mcts.csv", index=False)