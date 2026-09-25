import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_29/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_29/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, left_on="movie id", right_on="movie_id")

# Group by the leftmost columns (unique identifiers) and aggregate rating by max
result = merged.groupby(
    ["movie title", "movie id", "user_id", "movie_id"], as_index=False
).agg({"rating": "max"})

# Reorder columns to match target schema exactly
result = result[["movie title", "movie id", "user_id", "movie_id", "rating"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_29/target_multisource_mcts.csv", index=False)