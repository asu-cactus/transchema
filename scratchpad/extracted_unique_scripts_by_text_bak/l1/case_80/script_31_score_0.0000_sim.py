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

target_df = union_df[['movieId', 'rating']].copy()
target_df['movieId'] = target_df['movieId'].astype(int)
target_df['rating'] = target_df['rating'].astype(float)

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)