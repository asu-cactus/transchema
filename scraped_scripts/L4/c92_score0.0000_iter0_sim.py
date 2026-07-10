import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_92/training_2.csv", index_col=0)

src0['gender'] = src0['gender'].map({'M':1, 'F':2}).fillna(0).astype(int)
src0['zip'] = src0['zip'].astype(str).str.extract('(\d+)').astype(int)

joined_1_2 = pd.merge(src1, src2, on='movie_id', how='inner', suffixes=('_x', '_y'))
final = pd.merge(joined_1_2, src0, on='user_id', how='inner')

final = final.rename(columns={
    'genres_x': 'genres_x',
    'genres_y': 'genres_y',
    'movie_id_x': 'movie_id_x',
    'movie_id_y': 'movie_id_y'
})

final = final[['title', 'user_id', 'movie_id_x', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'genres_x', 'movie_id_y', 'genres_y']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_92/target_multisource_mcts.csv", index=False)