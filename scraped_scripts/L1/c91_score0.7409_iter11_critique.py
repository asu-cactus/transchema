import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_91/training_0.csv", index_col=0)

# Normalize string columns by lowercasing to match target examples
for col in ['Name', 'Position', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season']:
    df[col] = df[col].astype(str).str.lower()

# Convert Age and Transfer_fee to nullable integer type
df['Age'] = pd.to_numeric(df['Age'], errors='coerce').astype('Int64')
df['Transfer_fee'] = pd.to_numeric(df['Transfer_fee'], errors='coerce').astype('Int64')

# Convert Market_value to float (already float, but ensure NaNs are preserved)
df['Market_value'] = pd.to_numeric(df['Market_value'], errors='coerce').astype(float)

# Ensure columns have correct types and names exactly as target schema
df = df[['Name', 'Position', 'Age', 'Team_from', 'League_from', 'Team_to', 'League_to', 'Season', 'Market_value', 'Transfer_fee']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_91/target_multisource_mcts.csv", index=False)