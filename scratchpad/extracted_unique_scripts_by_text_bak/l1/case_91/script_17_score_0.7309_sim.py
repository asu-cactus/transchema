import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

df['Position'] = df['Position'].astype(str)
df['Team_from'] = df['Team_from'].astype(str)
df['League_from'] = df['League_from'].astype(str)
df['Team_to'] = df['Team_to'].astype(str)
df['League_to'] = df['League_to'].astype(str)
df['Season'] = df['Season'].astype(str)

df['Name'] = df['Name'].astype(str)
df['Age'] = pd.to_numeric(df['Age'], errors='coerce').astype('Int64')
df['Market_value'] = pd.to_numeric(df['Market_value'], errors='coerce')
df['Transfer_fee'] = pd.to_numeric(df['Transfer_fee'], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)