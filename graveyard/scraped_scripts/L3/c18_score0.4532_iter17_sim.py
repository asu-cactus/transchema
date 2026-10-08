import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_18/training_2.csv", index_col=0)

joined_0 = pd.merge(source2, source1, on="movie_id", how="inner")
joined_1 = pd.merge(joined_0, source0, on="user_id", how="inner")

result = joined_1[["title", "user_id", "movie_id", "rating", "timestamp", "age", "occupation"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_18/target_multisource_mcts.csv", index=False)