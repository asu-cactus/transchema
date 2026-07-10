import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

# Convert gender to integer codes
s0['gender'] = s0['gender'].astype('category').cat.codes

# Join s0 and s1 on user_id
joined_01 = pd.merge(s0, s1, on='user_id', how='inner')

# Join the above with s2 on movie_id
joined_all = pd.merge(joined_01, s2, on='movie_id', how='inner')

# Convert zip to integer by removing non-digit characters
def zip_to_int(z):
    if pd.isna(z):
        return pd.NA
    z_str = str(z)
    digits = ''.join(filter(str.isdigit, z_str))
    if digits == '':
        return pd.NA
    return int(digits)

joined_all['zip'] = joined_all['zip'].apply(zip_to_int)

# Create genres_x as categorical codes of genres (genres_y is string from s2)
joined_all['genres_x'] = joined_all['genres'].astype('category').cat.codes

# Rename columns to match target schema exactly
# movie_id_x from s1/s0 side (original movie_id)
# movie_id_y duplicate of movie_id_x
# genres_y is original genres string from s2
joined_all = joined_all.rename(columns={
    'movie_id': 'movie_id_x',
    'genres': 'genres_y'
})

joined_all['movie_id_y'] = joined_all['movie_id_x']

# Select and reorder columns as per target schema
result = joined_all[[
    'title',         # string
    'user_id',       # int
    'movie_id_x',    # int
    'rating',        # int
    'timestamp',     # int
    'gender',        # int
    'age',           # int
    'occupation',    # int
    'zip',           # int
    'genres_x',      # int
    'movie_id_y',    # int
    'genres_y'       # string
]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)