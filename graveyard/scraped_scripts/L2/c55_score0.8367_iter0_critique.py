import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_55/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_55/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="movieId", how="inner")

# Group by movieId, title, genres and aggregate userId and rating by mean
result = merged.groupby(["movieId", "title", "genres"], as_index=False).agg({
    "userId": "mean",
    "rating": "mean"
})

# Ensure correct types
result["movieId"] = result["movieId"].astype(int)
result["title"] = result["title"].astype(str)
result["genres"] = result["genres"].astype(str)
result["userId"] = result["userId"].astype(float)
result["rating"] = result["rating"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_55/target_multisource_mcts.csv", index=False)