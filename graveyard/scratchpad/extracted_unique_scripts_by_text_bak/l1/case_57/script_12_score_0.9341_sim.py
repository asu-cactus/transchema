import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_57/training_0.csv", index_col=0)

df_union = pd.concat([df0], ignore_index=True)

result = df_union.groupby("movieId", as_index=False)["rating"].mean()
result["movieId"] = result["movieId"].astype(int)
result["rating"] = result["rating"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_57/target_multisource_mcts.csv", index=False)