import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_2.csv", index_col=0)

agg = source2.groupby("movie id", as_index=False).agg({"rating": "min"})

joined = pd.merge(source0, agg, how="inner", left_on="movie id", right_on="movie id")

result = joined[["movie title", "rating"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_97/target_multisource_mcts.csv", index=False)