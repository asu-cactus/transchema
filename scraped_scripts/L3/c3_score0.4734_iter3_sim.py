import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_2.csv", index_col=0)

joined_0 = pd.merge(df2, df0, how="inner", on="user_id")
joined_1 = pd.merge(joined_0, df1, how="inner", on="movie_id")

result = joined_1.groupby(
    ["title", "user_id", "age", "occupation", "movie_id"],
    as_index=False
).agg({
    "rating": "mean",
    "timestamp": "mean"
})

result = result[["title", "user_id", "age", "occupation", "movie_id", "rating", "timestamp"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_3/target_multisource_mcts.csv", index=False)