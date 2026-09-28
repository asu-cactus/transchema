import pandas as pd
import numpy as np

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

# Normalize 'Name' to lowercase to match target examples
df['Name'] = df['Name'].str.lower()

# Cast 'Age' to integer (Int64 to allow NaN if any)
df['Age'] = df['Age'].astype('Int64')

# 'Market_value' is float, keep as is
df['Market_value'] = df['Market_value'].astype(float)

# 'Transfer_fee' to integer (Int64 to allow NaN if any)
df['Transfer_fee'] = df['Transfer_fee'].astype('Int64')

# Ensure column order matches target schema exactly
result = df[['Name', 'Position', 'Age', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season', 'Market_value', 'Transfer_fee']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)