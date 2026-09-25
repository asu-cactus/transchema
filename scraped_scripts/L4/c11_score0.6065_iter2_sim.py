import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_11/training_2.csv", index_col=0)

df1_unpivot = df1.melt(id_vars=['movie_id'], value_vars=['title', 'genres'], var_name='title_y', value_name='value')
# The unpivot creates rows with title_y = 'title' or 'genres' and value = corresponding string
# But target schema expects title_y and genres_y as separate columns, so we pivot back by movie_id and title_y grouping

# Pivot back to get title_y and genres_y columns per movie_id
df1_pivot = df1_unpivot.pivot(index='movie_id', columns='title_y', values='value').reset_index()
df1_pivot.columns.name = None

# Rename columns to match target: title_y, genres_y
df1_pivot = df1_pivot.rename(columns={'title': 'title_y', 'genres': 'genres_y'})

# Join df1_pivot with df2 on movie_id
df_join_1 = pd.merge(df2, df1_pivot, on='movie_id', how='inner')

# Join df_join_1 with df0 on user_id
df_join_2 = pd.merge(df_join_1, df0, on='user_id', how='inner')

# The target schema is:
# ['movie_id': int, 'user_id': int, 'rating': int, 'timestamp': int, 'gender': int, 'age': int, 'occupation': int, 'zip': int, 'title_x': int, 'genres_x': int, 'title_y': string, 'genres_y': string]

# We have movie_id, user_id, rating, timestamp, gender, age, occupation, zip, title_y, genres_y

# The target has title_x and genres_x as integer columns, but source1 only has title and genres as strings.
# The target examples show title_x and genres_x as integers, likely representing some encoding or counts.

# Since no source table has title_x or genres_x, we must create them.

# We can create title_x and genres_x as integer encodings of title_y and genres_y respectively.

# For title_x, encode title_y as categorical codes
df_join_2['title_x'] = df_join_2['title_y'].astype('category').cat.codes + 1

# For genres_x, encode genres_y as categorical codes
df_join_2['genres_x'] = df_join_2['genres_y'].astype('category').cat.codes + 1

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

# Select and reorder columns to match target schema
result = df_join_2[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x', 'title_y', 'genres_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_11/target_multisource_mcts.csv", index=False)