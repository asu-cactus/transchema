import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

union_1_2 = pd.merge(source1, source2, on="user_id", how="inner")

result = pd.merge(union_1_2, source0, on="movie_id", how="inner")

final = result[["title", "movie_id", "video_release_date", "user_id", "rating", "unix_timestamp", "age"]]

final["movie_id"] = final["movie_id"].astype("Int64")
final["video_release_date"] = pd.to_numeric(final["video_release_date"], errors='coerce')
final["user_id"] = pd.to_numeric(final["user_id"], errors='coerce')
final["rating"] = pd.to_numeric(final["rating"], errors='coerce')
final["unix_timestamp"] = pd.to_numeric(final["unix_timestamp"], errors='coerce')
final["age"] = pd.to_numeric(final["age"], errors='coerce')

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)