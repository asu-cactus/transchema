import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

join_01 = pd.merge(df0, df1, on="movie_id", how="inner")
join_all = pd.merge(join_01, df2, on="user_id", how="inner")

result = join_all[["title", "movie_id", "video_release_date", "user_id", "rating", "unix_timestamp", "age"]].copy()

result["movie_id"] = result["movie_id"].astype("Int64")
result["user_id"] = result["user_id"].astype(float)
result["rating"] = result["rating"].astype(float)
result["unix_timestamp"] = result["unix_timestamp"].astype(float)
result["age"] = result["age"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)