import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)

join_1_2 = pd.merge(source1, source2, on="user_id", how="inner")

joined_all = pd.merge(source0, join_1_2, on="movie_id", how="inner")

result = pd.DataFrame()
result["title"] = joined_all["title"].astype(str)
result["movie_id"] = joined_all["movie_id"].astype(int)
result["video_release_date"] = pd.to_numeric(joined_all["video_release_date"], errors='coerce')
result["user_id"] = pd.to_numeric(joined_all["user_id"], errors='coerce')
result["rating"] = pd.to_numeric(joined_all["rating"], errors='coerce')
result["unix_timestamp"] = pd.to_numeric(joined_all["unix_timestamp"], errors='coerce')
result["age"] = pd.to_numeric(joined_all["age"], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)