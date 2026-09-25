import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv", index_col=0)
df0['user_id'] = df0['user_id'].str.lower()
df0_grouped = df0.groupby('user_id', as_index=False).agg({'email':'first', 'geo':'first'})
df0_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)