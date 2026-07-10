import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)
df0['Name'] = df0['Name'].str.lower()
df0['Age'] = df0['Age'].astype(int)
df0['Market_value'] = df0['Market_value'].astype(float)
df0['Transfer_fee'] = df0['Transfer_fee'].astype(int)
df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)