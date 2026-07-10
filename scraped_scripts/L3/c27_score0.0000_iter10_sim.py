import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_2.csv", index_col=0)

join_1_2 = pd.merge(source1, source2, on="movie_id", how="inner")
final_join = pd.merge(source0, join_1_2, on=["user_id", "movie_id"], how="inner")

result = final_join[["title", "user_id", "movie_id", "rating", "timestamp", "age", "occupation"]].copy()

result["title"] = result["title"].astype(str)
result["user_id"] = result["user_id"].astype(float)
result["movie_id"] = result["movie_id"].astype(int)
result["rating"] = result["rating"].astype(float)
result["timestamp"] = result["timestamp"].astype(float)
result["age"] = result["age"].astype(float)
result["occupation"] = result["occupation"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_27/target_multisource_mcts.csv", index=False)