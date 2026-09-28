import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_2.csv", index_col=0)

joined_1 = pd.merge(df2, df0, on="user_id", how="inner")
joined_2 = pd.merge(joined_1, df1, on="movie_id", how="inner")

grouped = joined_2.groupby(["title", "movie_id"], as_index=False).agg({
    "user_id": "mean",
    "rating": "mean",
    "timestamp": "mean",
    "age": "mean",
    "occupation": "mean"
})

grouped = grouped[["title", "user_id", "movie_id", "rating", "timestamp", "age", "occupation"]]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_18/target_multisource_mcts.csv", index=False)