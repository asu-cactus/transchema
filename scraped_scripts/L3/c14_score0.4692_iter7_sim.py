import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_2.csv", index_col=0)

agg = source1.merge(source2, on="user_id", how="inner")
agg_grouped = agg.groupby(["user_id", "movie_id"], as_index=False).agg({
    "rating": "mean",
    "timestamp": "mean",
    "age": "mean",
    "occupation": "mean"
})

result = agg_grouped.merge(source0[["movie_id", "title"]], on="movie_id", how="inner")

result = result[["title", "user_id", "movie_id", "rating", "timestamp", "age", "occupation"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_14/target_multisource_mcts.csv", index=False)