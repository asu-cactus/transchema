import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv", index_col=0)

df0['user_id'] = df0['user_id'].astype(str)
df0['email'] = df0['email'].astype(str)
df0['geo'] = df0['geo'].astype(str)

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)