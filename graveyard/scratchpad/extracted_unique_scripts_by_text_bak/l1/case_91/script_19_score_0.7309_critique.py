import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

# Convert columns to target schema types:
# 'Name': string
df0['Name'] = df0['Name'].astype(str)

# 'Position': string
df0['Position'] = df0['Position'].astype(str)

# 'Age': integer (int64)
df0['Age'] = pd.to_numeric(df0['Age'], errors='coerce').astype('Int64')

# 'Team_from': string
df0['Team_from'] = df0['Team_from'].astype(str)

# 'League_from': string
df0['League_from'] = df0['League_from'].astype(str)

# 'Team_to': string
df0['Team_to'] = df0['Team_to'].astype(str)

# 'League_to': string
df0['League_to'] = df0['League_to'].astype(str)

# 'Season': string
df0['Season'] = df0['Season'].astype(str)

# 'Market_value': float (may contain NaN)
df0['Market_value'] = pd.to_numeric(df0['Market_value'], errors='coerce').astype(float)

# 'Transfer_fee': integer (int64)
df0['Transfer_fee'] = pd.to_numeric(df0['Transfer_fee'], errors='coerce').astype('Int64')

# Output with exact target schema and column order
result = df0[['Name', 'Position', 'Age', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season', 'Market_value', 'Transfer_fee']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)