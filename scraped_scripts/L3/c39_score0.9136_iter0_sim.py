import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_39/training_1.csv", index_col=0)

result = df1.groupby("movieId", as_index=False)["rating"].mean()
result["movieId"] = result["movieId"].astype(int)
result["rating"] = result["rating"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_39/target_multisource_mcts.csv", index=False)