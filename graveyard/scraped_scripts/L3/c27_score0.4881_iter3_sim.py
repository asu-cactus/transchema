import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_2.csv", index_col=0)

join_0_2 = pd.merge(df0, df2, on="movie_id", how="inner")
join_all = pd.merge(join_0_2, df1, on="user_id", how="inner")

result = join_all[["title", "user_id", "movie_id", "rating", "timestamp", "age", "occupation"]].copy()

result["user_id"] = result["user_id"].astype(float)
result["movie_id"] = result["movie_id"].astype(int)
result["rating"] = result["rating"].astype(float)
result["timestamp"] = result["timestamp"].astype(float)
result["age"] = result["age"].astype(float)
result["occupation"] = result["occupation"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_27/target_multisource_mcts.csv", index=False)