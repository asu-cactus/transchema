import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_2.csv", index_col=0)

join_1_2 = pd.merge(source1, source2, on="movie_id", how="inner")
full_join = pd.merge(join_1_2, source0, on="user_id", how="inner")

grouped = full_join.groupby(["title", "user_id", "movie_id"], as_index=False).agg({
    "rating": "mean",
    "timestamp": "mean",
    "age": "mean",
    "occupation": "mean"
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_32/target_multisource_mcts.csv", index=False)