import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_80/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

union_df = pd.concat(dfs, ignore_index=True)

# Group by movieId and aggregate rating by mean
target_df = union_df.groupby('movieId', as_index=False)['rating'].mean()

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)