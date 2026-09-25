import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_80/training_0.csv", index_col=0)

df_union = pd.concat([source0, source0], ignore_index=True)

target = df_union[['movieId', 'rating']].copy()
target['movieId'] = target['movieId'].astype(int)
target['rating'] = target['rating'].astype(float)

target.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)