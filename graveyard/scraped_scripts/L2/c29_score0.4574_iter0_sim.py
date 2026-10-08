import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_29/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_29/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, left_on="movie id", right_on="movie_id", how="inner")

result = merged.rename(columns={"movie title": "movie title", "movie id": "movie id", "user_id": "user_id", "movie_id": "movie_id", "rating": "rating"})[
    ["movie title", "movie id", "user_id", "movie_id", "rating"]
]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_29/target_multisource_mcts.csv", index=False)