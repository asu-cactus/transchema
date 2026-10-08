import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_2.csv", index_col=0)

merged = pd.merge(source2, source1, left_on="movie id", right_on="movie id", how="inner")
grouped = merged.groupby("movie title", as_index=False)["rating"].mean()
grouped = grouped.rename(columns={"movie title": "movie title", "rating": "rating"})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_6/target_multisource_mcts.csv", index=False)