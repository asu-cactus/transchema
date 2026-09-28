import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_30/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_30/training_1.csv", index_col=0)

joined = pd.merge(
    source0,
    source1,
    on="movieId",
    how="inner"
)

target = joined[["movieId", "title", "genres", "userId", "tag", "timestamp"]]

target["movieId"] = target["movieId"].astype(int)
target["userId"] = target["userId"].astype(int)
target["timestamp"] = target["timestamp"].astype(int)
target["title"] = target["title"].astype(str)
target["genres"] = target["genres"].astype(str)
target["tag"] = target["tag"].astype(str)

target.to_csv("autopipeline-benchmarks/github-pipelines/length1_30/target_multisource_mcts.csv", index=False)