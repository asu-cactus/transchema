import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_2.csv", index_col=0)

joined_0 = pd.merge(src2, src0, on="user_id", how="inner")
joined_1 = pd.merge(joined_0, src1, on="movie_id", how="inner")

result = joined_1[["title", "user_id", "age", "occupation", "movie_id", "rating", "timestamp"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_3/target_multisource_mcts.csv", index=False)