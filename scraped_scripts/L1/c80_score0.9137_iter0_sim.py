import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_80/training_0.csv", index_col=0)
grouped = df0.groupby("movieId", as_index=False)["rating"].mean()
grouped["movieId"] = grouped["movieId"].astype(int)
grouped["rating"] = grouped["rating"].astype(float)
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)