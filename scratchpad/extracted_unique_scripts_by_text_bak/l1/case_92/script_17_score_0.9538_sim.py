import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv", index_col=0)

result = df0.groupby(['user_id', 'email', 'geo'], dropna=False).size().reset_index(name='count')

result = result[['user_id', 'email', 'geo']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)