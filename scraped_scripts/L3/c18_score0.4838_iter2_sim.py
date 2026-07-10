import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_2.csv", index_col=0)

join_1 = pd.merge(source2, source1, on="movie_id", how="inner")
join_2 = pd.merge(join_1, source0, on="user_id", how="inner")

agg = join_2.groupby(["title", "user_id", "movie_id"], as_index=False).agg({
    "rating": "mean",
    "timestamp": "mean",
    "age": "mean",
    "occupation": "mean"
})

agg = agg.rename(columns={
    "rating": "rating",
    "timestamp": "timestamp",
    "age": "age",
    "occupation": "occupation"
})

agg["user_id"] = agg["user_id"].astype(float)
agg["movie_id"] = agg["movie_id"].astype(int)
agg["rating"] = agg["rating"].astype(float)
agg["timestamp"] = agg["timestamp"].astype(float)
agg["age"] = agg["age"].astype(float)
agg["occupation"] = agg["occupation"].astype(float)
agg["title"] = agg["title"].astype(str)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_18/target_multisource_mcts.csv", index=False)