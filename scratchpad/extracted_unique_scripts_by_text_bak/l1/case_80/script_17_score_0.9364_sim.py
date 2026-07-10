import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_80/training_0.csv", index_col=0)
grouped = df0.groupby("movieId").agg(rating_sum=("rating", "sum"), user_count=("userId", "count")).reset_index()
grouped["rating"] = grouped["rating_sum"] / grouped["user_count"]
result = grouped[["movieId", "rating"]]
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)