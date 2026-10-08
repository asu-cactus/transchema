import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_15/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="movieId", how="inner")

merged['genres_arr'] = merged['genres'].str.split('|')
merged['genre_count'] = merged['genres_arr'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else '')

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

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_15/target_multisource_mcts.csv", index=False)