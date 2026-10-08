import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

# Unpivot Source4_93_2: rating and timestamp are values, user_id and movie_id are keys
# Actually, unpivot here means melt rating and timestamp into rows? But target schema expects rating and timestamp as columns.
# The partial plan says UNPIVOT then GROUP_BY on movie_id, but target schema has rating and timestamp as columns.
# So likely the partial plan's 'UNPIVOT' means melting rating and timestamp into rows, but target schema expects them as columns.
# Given the target schema and sources, no unpivot is needed. Instead, we keep rating and timestamp as columns.
# So we skip unpivot and just join tables.

# Join s2 with s0 on user_id
df = s2.merge(s0, on='user_id', how='left')

# Join the above with s1 on movie_id
df = df.merge(s1, on='movie_id', how='left')

# Fix data types and column names to match target schema
# Target schema: ['movie_id': int, 'user_id': int, 'rating': int, 'timestamp': int, 'gender': int, 'age': int, 'occupation': int, 'zip': int, 'title_x': int, 'genres_x': int, 'title_y': string, 'genres_y': string]

# gender is string in source, target expects int - likely encoding gender to int
df['gender'] = df['gender'].map({'M':1, 'F':2}).fillna(0).astype(int)

# age, occupation are int but may be string in source, convert to int
df['age'] = pd.to_numeric(df['age'], errors='coerce').fillna(0).astype(int)
df['occupation'] = pd.to_numeric(df['occupation'], errors='coerce').fillna(0).astype(int)

# zip is string in source, target expects int - convert zip to int by removing non-digit chars and converting
df['zip'] = df['zip'].astype(str).str.extract('(\d+)').fillna('0').astype(int)

# title_x and genres_x are int in target but source s0 has no such columns, s1 has title and genres as string
# The target schema has title_x, genres_x as int and title_y, genres_y as string
# We have only one title and genres source (s1), so we create dummy int columns title_x and genres_x as counts or codes
# We can encode title and genres to int codes for title_x and genres_x
df['title_x'] = df['title'].astype('category').cat.codes + 1
df['genres_x'] = df['genres'].astype('category').cat.codes + 1

# title_y and genres_y are string, we can keep them as the original title and genres columns
df['title_y'] = df['title']
df['genres_y'] = df['genres']

# Select and reorder columns to match target schema
df_out = df[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip',
             'title_x', 'genres_x', 'title_y', 'genres_y']]

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)