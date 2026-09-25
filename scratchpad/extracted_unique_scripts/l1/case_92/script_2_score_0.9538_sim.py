import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv", index_col=0)

df = pd.concat([df0], ignore_index=True)

df['user_id'] = df['user_id'].astype(str)
df['email'] = df['email'].astype(str)
df['geo'] = df['geo'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)