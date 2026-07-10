import pandas as pd
import re

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

# Join df0 and df1 on user_id
joined_0 = pd.merge(df0, df1, on='user_id', how='inner')

# Join joined_0 with df2 to get title and genres_x (first join)
joined_1 = pd.merge(joined_0, df2, left_on='movie_id', right_on='movie_id', how='inner', suffixes=('_x', '_y'))

# Join joined_1 again with df2 to get movie_id_y and genres_y (second join)
# This join is on the same movie_id, but to produce the second set of movie_id and genres columns
joined_2 = pd.merge(joined_1, df2, left_on='movie_id', right_on='movie_id', how='inner', suffixes=('', '_y2'))

# Now rename columns to match target schema
# target schema: ['title': string, 'user_id': integer, 'movie_id_x': integer, 'rating': integer, 'timestamp': integer,
# 'gender': integer, 'age': integer, 'occupation': integer, 'zip': integer, 'genres_x': integer,
# 'movie_id_y': integer, 'genres_y': string]

# The first df2 join provides 'title' and 'genres' (genres_x)
# The second df2 join provides 'movie_id' (movie_id_y) and 'genres' (genres_y)

# Rename columns accordingly
final_df = joined_2.rename(columns={
    'title': 'title',
    'user_id': 'user_id',
    'movie_id_x': 'movie_id_x',  # from joined_1, but currently 'movie_id' column is ambiguous, so assign explicitly below
    'movie_id': 'movie_id_x',    # movie_id from first join is movie_id_x
    'rating': 'rating',
    'timestamp': 'timestamp',
    'gender': 'gender',
    'age': 'age',
    'occupation': 'occupation',
    'zip': 'zip',
    'genres_x': 'genres_x',      # will assign below
    'movie_id_y': 'movie_id_y',  # from second join
    'genres_y': 'genres_y'       # from second join
})

# Because suffixes were used, columns are:
# After first join: 'title', 'genres' (from df2) - these are genres_x
# After second join: 'movie_id_y' and 'genres_y' come from df2 with suffix '_y2'

# So explicitly assign:
final_df['movie_id_x'] = final_df['movie_id']  # from first join
final_df['genres_x'] = final_df['genres']     # from first join
final_df['movie_id_y'] = final_df['movie_id_y'] if 'movie_id_y' in final_df.columns else final_df['movie_id_y']
final_df['genres_y'] = final_df['genres_y'] if 'genres_y' in final_df.columns else final_df['genres_y']

# But the second join columns have suffix '_y2', so fix that:
if 'movie_id_y2' in final_df.columns:
    final_df['movie_id_y'] = final_df['movie_id_y2']
if 'genres_y2' in final_df.columns:
    final_df['genres_y'] = final_df['genres_y2']

# Drop duplicate or unnecessary columns
drop_cols = ['movie_id_y2', 'genres_y2', 'movie_id', 'genres']
for col in drop_cols:
    if col in final_df.columns:
        final_df = final_df.drop(columns=[col])

# Convert gender from string to integer (map 'M'->1, 'F'->0)
final_df['gender'] = final_df['gender'].map({'M': 1, 'F': 0})

# Convert zip to integer by removing non-digit characters
def zip_to_int(z):
    if pd.isna(z):
        return pd.NA
    digits = re.sub(r'\D', '', str(z))
    return int(digits) if digits else pd.NA

final_df['zip'] = final_df['zip'].apply(zip_to_int)

# Ensure correct column order as per target schema
final_df = final_df[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp',
                     'gender', 'age', 'occupation', 'zip', 'genres_x',
                     'movie_id_y', 'genres_y']]

# Group by title and user_id (leftmost columns) - no aggregation needed, just drop duplicates
final_df = final_df.drop_duplicates(subset=['title', 'user_id'])

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)