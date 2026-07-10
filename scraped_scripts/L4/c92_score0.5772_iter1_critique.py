import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

# Map gender to integer
source0['gender'] = source0['gender'].map({'M': 1, 'F': 2})

# Extract numeric part of zip and convert to int
source0['zip'] = source0['zip'].str.extract(r'(\d+)').astype(int)

# Join Source1 and Source0 on user_id
merged_01 = pd.merge(source1, source0, on='user_id', how='inner')

# Join merged_01 and Source2 on movie_id
merged_012 = pd.merge(merged_01, source2, on='movie_id', how='inner')

# Rename columns to match target schema
merged_012.rename(columns={'movie_id': 'movie_id_x', 'genres': 'genres_y'}, inplace=True)

# Create genres_x as categorical codes from rating side (or from merged_01 side)
# Since genres_x is integer and genres_y is string, genres_x likely corresponds to genres from Source1 side
# But Source1 has no genres, so genres_x should be derived from merged_01's movie_id_x or rating? 
# Actually, only Source2 has genres, so genres_x must be derived from genres_y (Source2 genres) as categorical codes
# But target has both genres_x (int) and genres_y (string). Possibly genres_x is categorical code of genres_y.

merged_012['genres_x'] = merged_012['genres_y'].astype('category').cat.codes + 1

# movie_id_y is same as movie_id_x (from Source2)
merged_012['movie_id_y'] = merged_012['movie_id_x']

# Select columns as per target schema
df = merged_012[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

# Group by title and user_id, aggregate others
agg_dict = {
    'movie_id_x': 'mean',
    'rating': 'mean',
    'timestamp': 'mean',
    'gender': 'mean',
    'age': 'mean',
    'occupation': 'mean',
    'zip': 'mean',
    'genres_x': 'mean',
    'movie_id_y': 'mean',
    'genres_y': 'first'
}

grouped = df.groupby(['title', 'user_id'], as_index=False).agg(agg_dict)

# Cast aggregated float columns back to int where appropriate
int_cols = ['movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y']
for col in int_cols:
    grouped[col] = grouped[col].round().astype(int)

# Reorder columns to match target schema exactly
grouped = grouped[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)