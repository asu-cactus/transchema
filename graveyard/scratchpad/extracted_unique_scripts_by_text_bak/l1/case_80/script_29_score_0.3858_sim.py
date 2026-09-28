import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_80/training_0.csv", index_col=0)
df_union = pd.concat([df0, df0], ignore_index=True)
df_target = df_union[['movieId', 'rating']]
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)