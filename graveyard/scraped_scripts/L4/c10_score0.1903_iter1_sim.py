import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_2.csv", index_col=0)

source0['movie_id'] = pd.NA
source0['rating'] = pd.NA
source0['timestamp'] = pd.NA

source1['age'] = pd.NA
source1['gender'] = pd.NA
source1['occupation'] = pd.NA
source1['zip'] = pd.NA

union_result = pd.concat([source0, source1], ignore_index=True, sort=False)

union_result['movie_id'] = pd.to_numeric(union_result['movie_id'], errors='coerce').astype('Int64')
union_result['user_id'] = pd.to_numeric(union_result['user_id'], errors='coerce').astype('Int64')
union_result['rating'] = pd.to_numeric(union_result['rating'], errors='coerce').astype('Int64')
union_result['timestamp'] = pd.to_numeric(union_result['timestamp'], errors='coerce').astype('Int64')
union_result['age'] = pd.to_numeric(union_result['age'], errors='coerce').astype('Int64')
union_result['occupation'] = pd.to_numeric(union_result['occupation'], errors='coerce').astype('Int64')

source2['movie_id'] = pd.to_numeric(source2['movie_id'], errors='coerce').astype('Int64')
source2['year'] = source2['year'].astype(str)
source2['movie_title'] = source2['movie_title'].astype(str)

merged = pd.merge(union_result, source2, on='movie_id', how='left')

merged['gender'] = merged['gender'].map({'M': 1, 'F': 2}).astype('Int64')

merged['movie_title_x'] = merged['movie_id'].astype('Int64')
merged['year_x'] = merged['movie_id'].astype('Int64')

merged['movie_title_y'] = merged['movie_title']
merged['year_y'] = merged['year']

final_cols = ['movie_id', 'movie_title_x', 'year_x', 'user_id', 'rating', 'timestamp', 'age', 'gender', 'occupation', 'zip', 'movie_title_y', 'year_y']

result = merged[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_10/target_multisource_mcts.csv", index=False)