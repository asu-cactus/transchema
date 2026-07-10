import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)

union_1_2 = pd.merge(source2, source1, on="user_id", how="inner")

merged = pd.merge(union_1_2, source0, on="movie_id", how="inner")

result = pd.DataFrame()
result["title"] = merged["title"].astype(str)
result["movie_id"] = merged["movie_id"].astype(int)
result["video_release_date"] = pd.to_numeric(merged["video_release_date"], errors='coerce')
result["user_id"] = pd.to_numeric(merged["user_id"], errors='coerce')
result["rating"] = pd.to_numeric(merged["rating"], errors='coerce')
result["unix_timestamp"] = pd.to_numeric(merged["unix_timestamp"], errors='coerce')
result["age"] = pd.to_numeric(merged["age"], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)