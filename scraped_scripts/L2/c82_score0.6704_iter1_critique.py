import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_82/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_82/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, on="movieId", how="inner")

merged['genres_arr'] = merged['genres'].apply(lambda x: str(list(x.split('|'))) if pd.notna(x) else x)
merged['genre_count'] = merged['genres'].apply(lambda x: str(len(x.split('|'))) if pd.notna(x) else x)

merged = merged[['userId', 'movieId', 'rating', 'timestamp', 'title', 'genres', 'genres_arr', 'genre_count']]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_82/target_multisource_mcts.csv", index=False)