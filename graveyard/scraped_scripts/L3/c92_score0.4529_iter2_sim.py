import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)

joined_0 = pd.merge(source2, source1, on="user_id", how="inner")
joined_1 = pd.merge(joined_0, source0, on="movie_id", how="inner")

result = joined_1[["title", "movie_id", "video_release_date", "user_id", "rating", "unix_timestamp", "age"]].copy()

result["video_release_date"] = pd.to_numeric(result["video_release_date"], errors="coerce")
result["user_id"] = result["user_id"].astype(float)
result["rating"] = result["rating"].astype(float)
result["unix_timestamp"] = result["unix_timestamp"].astype(float)
result["age"] = result["age"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)