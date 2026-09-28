import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df['user_id'] = df['user_id'].astype(str)
df['email'] = df['email'].astype(str)
df['geo'] = df['geo'].astype(str)

df = df.groupby('user_id', as_index=False).agg({'email': 'first', 'geo': 'first'})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)