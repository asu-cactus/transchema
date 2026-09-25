import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

source0['gender'] = source0['gender'].map({'M':1, 'F':2})
source0['zip'] = source0['zip'].str.extract(r'(\d+)').astype(int)

merged_01 = pd.merge(source1, source0, on='user_id', how='inner')

merged_012 = pd.merge(merged_01, source2, left_on='movie_id', right_on='movie_id', how='inner')

merged_012['genres_x'] = merged_012['genres'].astype('category').cat.codes + 1
merged_012['genres_y'] = merged_012['genres']

merged_012.rename(columns={'movie_id': 'movie_id_x'}, inplace=True)
merged_012['movie_id_y'] = merged_012['movie_id_x']

result = merged_012[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)