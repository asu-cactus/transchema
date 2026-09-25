import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

# Join ratings with user info on user_id
df = pd.merge(df2, df0, on='user_id', how='inner')

# Join with movie info on movie_id
df = pd.merge(df, df1, on='movie_id', how='inner')

# Map gender to integer
df['gender'] = df['gender'].map({'M':1, 'F':0}).fillna(0).astype(int)

# Convert age, occupation to int
df['age'] = pd.to_numeric(df['age'], errors='coerce').fillna(0).astype(int)
df['occupation'] = pd.to_numeric(df['occupation'], errors='coerce').fillna(0).astype(int)

# Extract digits from zip and convert to int
df['zip'] = df['zip'].str.extract('(\d+)').fillna('0').astype(int)

# title_x: number of titles per movie (always 1)
df['title_x'] = 1

# genres_x: count of genres per movie (split by '|')
df['genres_x'] = df['genres'].str.count('\|') + 1

# title_y and genres_y are the original strings
df['title_y'] = df['title']
df['genres_y'] = df['genres']

# Select final columns in order
final_cols = ['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip',
              'title_x', 'genres_x', 'title_y', 'genres_y']

final_df = df[final_cols]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)