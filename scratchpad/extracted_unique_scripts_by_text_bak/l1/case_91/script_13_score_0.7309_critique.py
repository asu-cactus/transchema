import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

# Convert columns to correct types matching target schema
df['Name'] = df['Name'].astype(str)
df['Position'] = df['Position'].astype(str)
# Convert Age to integer, drop rows with NaN in Age to match target integer type
df = df.dropna(subset=['Age', 'Transfer_fee'])
df['Age'] = df['Age'].astype(int)
df['Team_from'] = df['Team_from'].astype(str)
df['League_from'] = df['League_from'].astype(str)
df['Team_to'] = df['Team_to'].astype(str)
df['League_to'] = df['League_to'].astype(str)
df['Season'] = df['Season'].astype(str)
df['Market_value'] = pd.to_numeric(df['Market_value'], errors='coerce').astype(float)
df['Transfer_fee'] = df['Transfer_fee'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)