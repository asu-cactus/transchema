import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_55/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_55/training_1.csv", index_col=0)

agg = df0.groupby("movieId").agg(
    userId=("userId", "nunique"),
    rating_min=("rating", "min"),
    rating_max=("rating", "max")
).reset_index()

agg["rating"] = (agg["rating_min"] + agg["rating_max"]) / 2
agg = agg.drop(columns=["rating_min", "rating_max"])

result = pd.merge(df1, agg, on="movieId", how="inner")

result = result.rename(columns={"userId": "userId", "rating": "rating"})

result = result[["movieId", "title", "genres", "userId", "rating"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_55/target_multisource_mcts.csv", index=False)