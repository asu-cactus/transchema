import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

join_1_2 = pd.merge(source1, source2, how="inner", on="movie_id", suffixes=('_x', '_y'))
final = pd.merge(join_1_2, source0, how="inner", on="user_id")

final = final.rename(columns={
    'genres_x': 'genres_x',
    'genres_y': 'genres_y',
    'movie_id_x': 'movie_id_x',
    'movie_id_y': 'movie_id_y'
})

final = final[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

final['gender'] = final['gender'].map({'M': 1, 'F': 0}).fillna(0).astype(int)
final['age'] = pd.to_numeric(final['age'], errors='coerce').fillna(0).astype(int)
final['occupation'] = pd.to_numeric(final['occupation'], errors='coerce').fillna(0).astype(int)
final['zip'] = final['zip'].astype(str).str.extract('(\d+)').fillna('0').astype(int)
final['genres_x'] = final['genres_x'].astype(str).apply(lambda x: len(x.split('|')) if x else 0).astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)