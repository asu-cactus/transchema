import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

union_result = pd.concat([source0, source0], ignore_index=True)

join_result_1 = pd.merge(union_result, source1, on="movie_id", how="inner")

final_join = pd.merge(join_result_1, source2, on="user_id", how="inner")

result = final_join[["title", "movie_id", "video_release_date", "user_id", "rating", "unix_timestamp", "age"]]

result["movie_id"] = result["movie_id"].astype("Int64")
result["video_release_date"] = pd.to_numeric(result["video_release_date"], errors='coerce')
result["user_id"] = pd.to_numeric(result["user_id"], errors='coerce')
result["rating"] = pd.to_numeric(result["rating"], errors='coerce')
result["unix_timestamp"] = pd.to_numeric(result["unix_timestamp"], errors='coerce')
result["age"] = pd.to_numeric(result["age"], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)