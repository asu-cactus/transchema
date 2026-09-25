import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_0.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_2.csv", index_col=0)

union_result = pd.concat([source0, source0], ignore_index=True)

joined = pd.merge(union_result, source2, on="movie id", how="inner")

target = joined[["movie title", "rating"]].copy()
target["movie title"] = target["movie title"].astype(str)
target["rating"] = target["rating"].astype(float)

target.to_csv("autopipeline-benchmarks/github-pipelines/length3_97/target_multisource_mcts.csv", index=False)