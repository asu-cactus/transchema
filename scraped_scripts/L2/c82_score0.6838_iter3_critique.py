import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_82/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_82/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, on="movieId", how="left")

merged['genres_arr'] = merged['genres'].str.split('|').apply(str)
merged['genre_count'] = merged['genres'].str.split('|').str[0].fillna('')

merged = merged.astype({
    'userId': 'int64',
    'movieId': 'int64',
    'rating': 'float64',
    'timestamp': 'int64',
    'title': 'string',
    'genres': 'string',
    'genres_arr': 'string',
    'genre_count': 'string'
})

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_82/target_multisource_mcts.csv", index=False)