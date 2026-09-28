import pandas as pd

# Read sources with index_col=0 as per instructions
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

# Join df2 (ratings) with df0 (users) on user_id using inner join to avoid NaNs in user info
df_join_1 = pd.merge(df2, df0, on='user_id', how='inner')

# Join the above with df1 (movies) on movie_id using inner join to avoid NaNs in movie info
df_join_2 = pd.merge(df_join_1, df1, on='movie_id', how='inner')

# Rename movie columns to match target schema
df_join_2 = df_join_2.rename(columns={
    'title': 'title_y',
    'genres': 'genres_y'
})

# Add title_x and genres_x as integer columns filled with 0 (no source data)
df_join_2['title_x'] = 0
df_join_2['genres_x'] = 0

# Map gender 'M'->1, 'F'->0, else NaN
df_join_2['gender'] = df_join_2['gender'].map({'M': 1, 'F': 0})

# Convert zip to integer by extracting first 5 digits
def zip_to_int(z):
    if pd.isna(z):
        return pd.NA
    s = str(z).split('-')[0]
    try:
        return int(s)
    except:
        return pd.NA

df_join_2['zip'] = df_join_2['zip'].apply(zip_to_int)

# Group by movie_id and user_id, aggregate other columns by taking first non-null value
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

df_grouped = df_join_2.groupby(['movie_id', 'user_id'], as_index=False).agg(agg_dict)

# Ensure correct dtypes as per target schema
df_grouped = df_grouped.astype({
    'movie_id': 'Int64',
    'user_id': 'Int64',
    'rating': 'Int64',
    'timestamp': 'Int64',
    'gender': 'Int64',
    'age': 'Int64',
    'occupation': 'Int64',
    'zip': 'Int64',
    'title_x': 'Int64',
    'genres_x': 'Int64',
    'title_y': 'string',
    'genres_y': 'string'
})

# Reorder columns exactly as target schema
df_grouped = df_grouped[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x', 'title_y', 'genres_y']]

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)