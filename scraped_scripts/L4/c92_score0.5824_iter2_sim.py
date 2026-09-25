import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

source0['gender'] = source0['gender'].map({'M':1, 'F':2})

join_1_2 = pd.merge(source1, source2, on='movie_id', how='inner', suffixes=('_y', '_z'))

final_join = pd.merge(source0, join_1_2, on='user_id', how='inner')

final_join = final_join.rename(columns={
    'genres_y': 'genres_y',
    'genres_z': 'genres_y',  # Actually genres from source2 is genres_y in target
    'movie_id': 'movie_id_y',
    'movie_id_y': 'movie_id_x',
    'title': 'title',
    'rating': 'rating',
    'timestamp': 'timestamp',
    'gender': 'gender',
    'age': 'age',
    'occupation': 'occupation',
    'zip': 'zip'
})

# The join_1_2 merge added suffixes _y and _z, but we want movie_id_x and genres_x from source1 and movie_id_y and genres_y from source2.
# Actually source1 has movie_id, rating, timestamp, user_id
# source2 has movie_id, title, genres
# After merge source1+source2 on movie_id, movie_id column remains, genres from source2 is 'genres', title is 'title'
# So suffixes are not needed for source1 and source2 join because only source2 has genres and title columns.
# So let's redo join_1_2 without suffixes.

join_1_2 = pd.merge(source1, source2, on='movie_id', how='inner')
final_join = pd.merge(source0, join_1_2, on='user_id', how='inner')

# Now rename columns to match target schema:
# target schema: ['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']
# We have movie_id from source1 (call it movie_id_x), genres from source1? No genres in source1, genres in source2 only.
# So movie_id_x = movie_id from source1
# genres_x = ??? source1 has no genres, so genres_x must come from source1? No.
# The target has movie_id_x and genres_x and movie_id_y and genres_y.
# We only have one movie_id column in source1 and source2.
# The partial plan says JOIN : [[Source4_92_0, Source4_92_2]] columns=[] which is not used here.
# But the target has movie_id_x and movie_id_y and genres_x and genres_y.
# So likely we need to join source1 and source2 twice to get two movie info sets.
# But source1 has only one movie_id column.
# The target examples show movie_id_x and movie_id_y are different columns.
# So likely source1 has two movie_id columns? No.
# The target example shows movie_id_x and movie_id_y are different.
# So maybe source1 has movie_id_x and source2 has movie_id_y.
# But source2 only has one movie_id column.
# The partial plan says JOIN : [[Source4_92_0, Source4_92_2]] columns=[] which is empty, meaning cross join? No.
# The partial plan says JOIN : [[Source4_92_0, Source4_92_2]] columns=[] and GROUP_BY : [title]
# But the target schema requires user info, rating info, and two movie info sets.
# The only way to get two movie info sets is to join source1 twice with source2 on different movie_id columns.
# But source1 has only one movie_id column.
# So maybe source1 has two movie_id columns? No.
# The target examples show movie_id_x and movie_id_y, genres_x and genres_y.
# So maybe source1 has movie_id_x and movie_id_y columns? No.
# The source schemas:
# Source0: user_id, gender, age, occupation, zip
# Source1: user_id, movie_id, rating, timestamp
# Source2: movie_id, title, genres
# So only one movie_id column in source1 and source2.
# So movie_id_x and genres_x come from source1 joined with source2 (movie info)
# movie_id_y and genres_y come from source2 joined with source1? No.
# The target examples show movie_id_x and genres_x are integers, but genres_x is integer? genres_x is integer in target schema, genres_y is string.
# So genres_x is integer, genres_y is string.
# So genres_x is probably a genre id or count, genres_y is genre string.
# So maybe source2 genres column is string, genres_y.
# genres_x is integer, maybe from source1 or source0? No.
# So maybe genres_x is a count or encoding of genres from source2.
# So we need to create genres_x as integer encoding of genres string from source2.
# So the plan:
# 1) Join source1 and source2 on movie_id to get movie info (title, genres)
# 2) Join source0 on user_id to get user info
# 3) Create genres_x as integer encoding of genres string (genres_y)
# 4) movie_id_x = movie_id from source1
# 5) movie_id_y = movie_id from source2 (same as movie_id_x)
# 6) genres_y = genres string from source2
# 7) genres_x = integer encoding of genres_y
# 8) gender map M->1, F->2
# 9) zip convert to integer (remove dashes)
# 10) cast all columns to correct types

# Implementing this now:

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

source0['gender'] = source0['gender'].map({'M':1, 'F':2})
source0['zip'] = source0['zip'].astype(str).str.replace('-', '', regex=False)
source0['zip'] = pd.to_numeric(source0['zip'], errors='coerce').fillna(0).astype(int)

join_1_2 = pd.merge(source1, source2, on='movie_id', how='inner')

df = pd.merge(source0, join_1_2, on='user_id', how='inner')

df['genres_x'] = df['genres'].astype('category').cat.codes + 1  # integer encoding starting from 1
df['movie_id_x'] = df['movie_id']
df['movie_id_y'] = df['movie_id']
df['genres_y'] = df['genres']

df = df.rename(columns={
    'title': 'title',
    'user_id': 'user_id',
    'rating': 'rating',
    'timestamp': 'timestamp',
    'gender': 'gender',
    'age': 'age',
    'occupation': 'occupation',
    'zip': 'zip'
})

df = df[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

df = df.astype({
    'title': str,
    'user_id': int,
    'movie_id_x': int,
    'rating': int,
    'timestamp': int,
    'gender': int,
    'age': int,
    'occupation': int,
    'zip': int,
    'genres_x': int,
    'movie_id_y': int,
    'genres_y': str
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)