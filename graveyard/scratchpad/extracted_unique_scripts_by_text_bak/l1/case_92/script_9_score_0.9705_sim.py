import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv", index_col=0)
df0['user_id'] = df0['user_id'].str.lower()
result = pd.concat([df0], ignore_index=True)
result = result[['user_id', 'email', 'geo']]
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)