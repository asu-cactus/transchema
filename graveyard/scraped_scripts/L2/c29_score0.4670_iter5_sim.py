import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_29/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_29/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, left_on="movie_id", right_on="movie id")

result = merged.rename(columns={"movie title": "movie title", "movie id": "movie id", "user_id": "user_id", "movie_id": "movie_id", "rating": "rating"})
result = result[["movie title", "movie id", "user_id", "movie_id", "rating"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_29/target_multisource_mcts.csv", index=False)