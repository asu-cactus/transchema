import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_57/training_0.csv", index_col=0)
result = df0[['movieId', 'rating']].copy()
result['movieId'] = result['movieId'].astype(int)
result['rating'] = result['rating'].astype(float)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_57/target_multisource_mcts.csv", index=False)