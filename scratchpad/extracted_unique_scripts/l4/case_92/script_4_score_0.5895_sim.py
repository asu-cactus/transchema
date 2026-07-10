import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

s0['gender'] = s0['gender'].astype('category').cat.codes
s2['genres'] = s2['genres'].astype('category').cat.codes

joined_01 = pd.merge(s0, s1, on='user_id', how='inner')
joined_all = pd.merge(joined_01, s2, on='movie_id', how='inner')

agg = joined_all.groupby(['gender', 'genres']).agg(
    rating_count=('rating', 'count'),
    age_avg=('age', 'mean'),
    movie_id_count_distinct=('movie_id', pd.Series.nunique)
).reset_index()

# The aggregation is not directly needed for the final target schema, so we proceed with the full join data.

# The target schema columns:
# ['title': string, 'user_id': integer, 'movie_id_x': integer, 'rating': integer, 'timestamp': integer,
#  'gender': integer, 'age': integer, 'occupation': integer, 'zip': integer,
#  'genres_x': integer, 'movie_id_y': integer, 'genres_y': string]

# We have:
# s2: movie_id, title, genres (genres_y string)
# s1: user_id, movie_id, rating, timestamp
# s0: user_id, gender (converted to int), age, occupation, zip
# We need to produce movie_id_x and movie_id_y, genres_x and genres_y

# The target has movie_id_x and movie_id_y, and genres_x and genres_y.
# The source has only one movie_id column per table.
# We can interpret movie_id_x and genres_x as from s1 (joined_all), and movie_id_y and genres_y from s2.

# So we rename columns accordingly.

joined_all = joined_all.rename(columns={
    'movie_id': 'movie_id_x',
    'genres': 'genres_y',
    'title': 'title'
})

# genres_x is integer in target, so we can use the categorical codes of genres from s2 as genres_y (string) and genres_x from s1 side.
# But s1 has no genres column, so genres_x likely comes from s2 genres codes or from s2 genres codes duplicated.

# To get genres_x as integer, we can use the categorical codes of genres from s2 again, but since genres_y is string, genres_x is integer code.

# We already converted s2['genres'] to categorical codes in s2['genres'] before merge, but after merge genres column is renamed to genres_y (string).
# So we need to add genres_x as integer code of genres string.

# Let's create genres_x as categorical codes of genres_y string.

joined_all['genres_x'] = joined_all['genres_y'].astype('category').cat.codes

# movie_id_y is integer, so we can duplicate movie_id_x as movie_id_y.

joined_all['movie_id_y'] = joined_all['movie_id_x']

# gender is already integer coded.

# zip is string in source, but target expects integer. We convert zip to integer by removing non-digit characters and converting to int if possible, else NaN.

def zip_to_int(z):
    if pd.isna(z):
        return pd.NA
    z_str = str(z)
    digits = ''.join(filter(str.isdigit, z_str))
    if digits == '':
        return pd.NA
    return int(digits)

joined_all['zip'] = joined_all['zip'].apply(zip_to_int)

# Select and reorder columns to match target schema

result = joined_all[[
    'title',
    'user_id',
    'movie_id_x',
    'rating',
    'timestamp',
    'gender',
    'age',
    'occupation',
    'zip',
    'genres_x',
    'movie_id_y',
    'genres_y'
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)