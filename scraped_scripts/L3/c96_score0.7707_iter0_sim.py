import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_96/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_96/training_1.csv"
source2_path = "autopipeline-benchmarks/github-pipelines/length3_96/training_2.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length3_96/target_multisource_mcts.csv"

source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)
source2 = pd.read_csv(source2_path, index_col=0)

grouped_source2 = source2.groupby('movie id').agg({
    'user id': 'first',
    'rating': 'first',
    'timestamp': 'first'
}).reset_index()

joined_1 = pd.merge(grouped_source2, source1, how='inner', on='movie id')

final_join = pd.merge(joined_1, source0, how='inner', on='user id')

final = final_join.rename(columns={'Romance ': 'Romance'})

cols = ['movie title', 'movie id', 'release date', 'video release date', 'IMDb URL', 'unknown', 'Action', 'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western', 'user id', 'rating', 'timestamp', 'age', 'gender', 'occupation', 'zip code']

final = final[cols]

final['release date'] = pd.to_numeric(final['release date'], errors='coerce').fillna(0).astype(int)
final['video release date'] = pd.to_numeric(final['video release date'], errors='coerce').fillna(0).astype(int)
final['IMDb URL'] = final['IMDb URL'].astype('category').cat.codes
final['unknown'] = final['unknown'].astype(int)
genre_cols = ['Action', 'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
for col in genre_cols:
    final[col] = final[col].astype(int)
final['user id'] = final['user id'].astype(int)
final['rating'] = final['rating'].astype(int)
final['timestamp'] = final['timestamp'].astype(int)
final['age'] = final['age'].astype(int)
final['gender'] = final['gender'].map({'M': 1, 'F': 0}).fillna(-1).astype(int)
final['occupation'] = final['occupation'].astype('category').cat.codes
final['zip code'] = final['zip code'].astype('category').cat.codes

final.to_csv(target_path, index=False)