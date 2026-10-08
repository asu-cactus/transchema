import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_80/training_0.csv", index_col=0)

result = df0.groupby("movieId", as_index=False)["rating"].mean()
result["rating"] = result["rating"].astype(float)
result["movieId"] = result["movieId"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)