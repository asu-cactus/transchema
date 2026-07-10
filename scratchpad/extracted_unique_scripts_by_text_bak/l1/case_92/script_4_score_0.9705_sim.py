import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv", index_col=0)

df0.columns = [col.lower() for col in df0.columns]
df0['user_id'] = df0['user_id'].str.lower()

df0 = df0.rename(columns={'user_id': 'user_id', 'email': 'email', 'geo': 'geo'})

df0 = df0[['user_id', 'email', 'geo']]

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)