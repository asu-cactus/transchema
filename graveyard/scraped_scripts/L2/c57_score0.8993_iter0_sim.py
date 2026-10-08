import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_57/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_57/training_1.csv", index_col=0)

merged0 = source0.merge(source1, on="movie_id", how="left")

grouped = merged0.groupby("title").agg(
    size=("rating", "count"),
    mean=("rating", "mean")
).reset_index()

grouped["size"] = grouped["size"].astype(int)
grouped["mean"] = grouped["mean"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_57/target_multisource_mcts.csv", index=False)