import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_57/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_57/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_57/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_57/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_57/training_4.csv"
]

dfs = [pd.read_csv(p) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)
result = df_all.groupby("movieId", as_index=False)["rating"].mean()
result["movieId"] = result["movieId"].astype(int)
result["rating"] = result["rating"].astype(float)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_57/target_multisource_mcts.csv", index=False)