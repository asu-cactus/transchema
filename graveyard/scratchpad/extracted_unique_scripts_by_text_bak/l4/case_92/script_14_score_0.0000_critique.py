import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

# Join Source1 and Source2 on movie_id
join_1_2 = pd.merge(source1, source2, how="inner", on="movie_id", suffixes=('_x', '_y'))

# Join the above with Source0 on user_id
final = pd.merge(join_1_2, source0, how="inner", on="user_id")

# Map gender to int
final['gender'] = final['gender'].map({'M': 1, 'F': 0}).fillna(0).astype(int)

# Convert age, occupation to int
final['age'] = pd.to_numeric(final['age'], errors='coerce').fillna(0).astype(int)
final['occupation'] = pd.to_numeric(final['occupation'], errors='coerce').fillna(0).astype(int)

# Extract numeric part of zip and convert to int
final['zip'] = final['zip'].astype(str).str.extract('(\d+)').fillna('0').astype(int)

# Convert genres_x to count of genres
final['genres_x'] = final['genres_x'].astype(str).apply(lambda x: len(x.split('|')) if x else 0).astype(int)

# Group by title and user_id, aggregate other columns by first value
agg_dict = {
    'movie_id_x': 'first',
    'rating': 'first',
    'timestamp': 'first',
    'gender': 'first',
    'age': 'first',
    'occupation': 'first',
    'zip': 'first',
    'genres_x': 'first',
    'movie_id_y': 'first',
    'genres_y': 'first'
}

final = final.groupby(['title', 'user_id'], as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
final = final[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)