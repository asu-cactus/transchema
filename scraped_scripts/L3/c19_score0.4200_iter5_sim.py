import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_2.csv", index_col=0)

union_result = pd.concat([source0, source0], ignore_index=True)

join_result_1 = pd.merge(union_result, source1, on="movie_id", how="inner")

join_result_2 = pd.merge(join_result_1, source2, on="user_id", how="inner")

result = join_result_2[["title", "user_id", "movie_id", "rating", "timestamp", "age", "occupation"]]

result["user_id"] = result["user_id"].astype(float)
result["movie_id"] = result["movie_id"].astype(int)
result["rating"] = result["rating"].astype(float)
result["timestamp"] = result["timestamp"].astype(float)
result["age"] = result["age"].astype(float)
result["occupation"] = result["occupation"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_19/target_multisource_mcts.csv", index=False)