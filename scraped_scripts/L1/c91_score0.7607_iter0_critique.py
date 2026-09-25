import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

df0['Age'] = df0['Age'].astype('Int64')
df0['Transfer_fee'] = df0['Transfer_fee'].astype('Int64')
df0['Market_value'] = df0['Market_value'].astype(float)

target_cols = ['Name', 'Position', 'Age', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season', 'Market_value', 'Transfer_fee']
df0 = df0[target_cols]

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)