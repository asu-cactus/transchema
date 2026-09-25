import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_55/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_55/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="movieId", how="inner")

result = merged[["movieId", "title", "genres", "userId", "rating"]].copy()
result["movieId"] = result["movieId"].astype(int)
result["title"] = result["title"].astype(str)
result["genres"] = result["genres"].astype(str)
result["userId"] = result["userId"].astype(float)
result["rating"] = result["rating"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_55/target_multisource_mcts.csv", index=False)