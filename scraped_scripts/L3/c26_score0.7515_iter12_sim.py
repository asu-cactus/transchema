import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_1.csv", index_col=0)

grouped = source0.groupby("movie_id", as_index=False)["rating"].sum()

merged = pd.merge(grouped, source1[["movie_id", "title"]], how="inner", on="movie_id")

result = merged[["title", "rating"]].rename(columns={"rating": "0"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_26/target_multisource_mcts.csv", index=False)