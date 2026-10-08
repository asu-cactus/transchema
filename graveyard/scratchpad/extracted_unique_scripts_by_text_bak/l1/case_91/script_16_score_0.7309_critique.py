import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

# Cast columns to match target schema types exactly
df['Name'] = df['Name'].astype(str)
df['Position'] = df['Position'].astype(str)
df['Age'] = df['Age'].astype('Int64')  # nullable integer
df['Team_from'] = df['Team_from'].astype(str)
df['League_from'] = df['League_from'].astype(str)
df['Team_to'] = df['Team_to'].astype(str)
df['League_to'] = df['League_to'].astype(str)
df['Season'] = df['Season'].astype(str)
df['Market_value'] = df['Market_value'].astype(float)
df['Transfer_fee'] = df['Transfer_fee'].astype('Int64')  # nullable integer

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)