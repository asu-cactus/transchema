import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_2.csv", index_col=0)

# Convert movie_id in source2 to Int64
source2['movie_id'] = pd.to_numeric(source2['movie_id'], errors='coerce').astype('Int64')
source2['year'] = source2['year'].astype(str)
source2['movie_title'] = source2['movie_title'].astype(str)

# Convert user_id and movie_id in source1 to Int64
source1['user_id'] = pd.to_numeric(source1['user_id'], errors='coerce').astype('Int64')
source1['movie_id'] = pd.to_numeric(source1['movie_id'], errors='coerce').astype('Int64')
source1['rating'] = pd.to_numeric(source1['rating'], errors='coerce').astype('Int64')
source1['timestamp'] = pd.to_numeric(source1['timestamp'], errors='coerce').astype('Int64')

# Convert user_id in source0 to Int64
source0['user_id'] = pd.to_numeric(source0['user_id'], errors='coerce').astype('Int64')
source0['age'] = pd.to_numeric(source0['age'], errors='coerce').astype('Int64')
source0['occupation'] = pd.to_numeric(source0['occupation'], errors='coerce').astype('Int64')
source0['zip'] = pd.to_numeric(source0['zip'], errors='coerce').astype('Int64')

# Map gender to int (M=1, F=2)
source0['gender'] = source0['gender'].map({'M': 1, 'F': 2}).astype('Int64')

# Join source1 (ratings) with source0 (user info) on user_id
merged = pd.merge(source1, source0, on='user_id', how='inner')

# Join merged with source2 (movie info) on movie_id
merged = pd.merge(merged, source2, on='movie_id', how='inner', suffixes=('_x', '_y'))

# Prepare final columns matching target schema:
# ['movie_id': int, 'movie_title_x': int, 'year_x': int, 'user_id': int, 'rating': int, 'timestamp': int,
#  'age': int, 'gender': int, 'occupation': int, 'zip': int, 'movie_title_y': string, 'year_y': string]

# movie_title_x and year_x in target are integers with values same as movie_id (from examples)
# So assign movie_title_x and year_x as movie_id (int)
merged['movie_title_x'] = merged['movie_id']
merged['year_x'] = merged['movie_id']

# movie_title_y and year_y come from source2 as strings
merged['movie_title_y'] = merged['movie_title']
merged['year_y'] = merged['year']

final_cols = ['movie_id', 'movie_title_x', 'year_x', 'user_id', 'rating', 'timestamp',
              'age', 'gender', 'occupation', 'zip', 'movie_title_y', 'year_y']

result = merged[final_cols]

# Ensure correct dtypes
result['movie_id'] = result['movie_id'].astype('Int64')
result['movie_title_x'] = result['movie_title_x'].astype('Int64')
result['year_x'] = result['year_x'].astype('Int64')
result['user_id'] = result['user_id'].astype('Int64')
result['rating'] = result['rating'].astype('Int64')
result['timestamp'] = result['timestamp'].astype('Int64')
result['age'] = result['age'].astype('Int64')
result['gender'] = result['gender'].astype('Int64')
result['occupation'] = result['occupation'].astype('Int64')
result['zip'] = result['zip'].astype('Int64')
result['movie_title_y'] = result['movie_title_y'].astype(str)
result['year_y'] = result['year_y'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_10/target_multisource_mcts.csv", index=False)