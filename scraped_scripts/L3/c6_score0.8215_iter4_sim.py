import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_2.csv", index_col=0)

agg_result = source2.groupby("movie id", as_index=False)["rating"].mean()

merged = pd.merge(agg_result, source1[["movie id", "movie title"]], on="movie id", how="inner")

result = merged[["movie title", "rating"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_6/target_multisource_mcts.csv", index=False)