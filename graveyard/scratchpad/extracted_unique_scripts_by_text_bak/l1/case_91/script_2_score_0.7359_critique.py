import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

# Lowercase 'Name' to match target examples
df0['Name'] = df0['Name'].astype(str).str.lower()

# Convert string columns
df0['Position'] = df0['Position'].astype(str)
df0['Team_from'] = df0['Team_from'].astype(str)
df0['League_from'] = df0['League_from'].astype(str)
df0['Team_to'] = df0['Team_to'].astype(str)
df0['League_to'] = df0['League_to'].astype(str)
df0['Season'] = df0['Season'].astype(str)

# Handle numeric columns
# Fill NaNs in Age and Transfer_fee with 0, then convert to int
df0['Age'] = pd.to_numeric(df0['Age'], errors='coerce').fillna(0).astype(int)
df0['Transfer_fee'] = pd.to_numeric(df0['Transfer_fee'], errors='coerce').fillna(0).astype(int)

# Market_value as float with NaNs allowed
df0['Market_value'] = pd.to_numeric(df0['Market_value'], errors='coerce').astype(float)

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)