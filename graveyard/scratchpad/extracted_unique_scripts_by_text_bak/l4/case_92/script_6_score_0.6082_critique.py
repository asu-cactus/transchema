import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

# Map gender to int
df0['gender'] = df0['gender'].map({'M':1, 'F':2}).fillna(0).astype(int)

# Extract numeric part of zip and convert to int
df0['zip'] = df0['zip'].str.extract('(\d+)').astype(int)

# Rename columns for clarity before join
df1 = df1.rename(columns={'movie_id': 'movie_id_x'})
df2 = df2.rename(columns={'movie_id': 'movie_id_y'})

# Join df1 and df0 on user_id
merged_1 = pd.merge(df1, df0, on='user_id', how='inner')

# Join merged_1 and df2 on movie_id_x = movie_id_y
merged_2 = pd.merge(merged_1, df2, left_on='movie_id_x', right_on='movie_id_y', how='inner')

# Group by title and user_id
agg_dict = {
    'movie_id_x': 'max',
    'rating': 'mean',
    'timestamp': 'max',
    'gender': 'max',
    'age': 'max',
    'occupation': 'max',
    'zip': 'max',
    'movie_id_y': 'max',
    'genres_y': 'first'
}

grouped = merged_2.groupby(['title', 'user_id'], as_index=False).agg(agg_dict)

# Count of ratings per group as genres_x
count_ratings = merged_2.groupby(['title', 'user_id']).size().reset_index(name='genres_x')

# Merge count into grouped
result = pd.merge(grouped, count_ratings, on=['title', 'user_id'], how='left')

# Round rating to int as target schema shows integer rating
result['rating'] = result['rating'].round().astype(int)

# Ensure all integer columns are int type
int_cols = ['user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y']
for col in int_cols:
    result[col] = result[col].astype(int)

# Reorder columns to match target schema
result = result[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)