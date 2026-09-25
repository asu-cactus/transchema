import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_0.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_2.csv", index_col=0)

grouped = source2.groupby("movie id", as_index=False)["rating"].mean()

merged = pd.merge(source0, grouped, how="inner", left_on="movie id", right_on="movie id")

result = merged[["movie title", "rating"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_97/target_multisource_mcts.csv", index=False)