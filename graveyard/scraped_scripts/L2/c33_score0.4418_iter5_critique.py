import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_33/training_1.csv", index_col=0)

# Convert numeric columns in df0
df0['bet'] = pd.to_numeric(df0['bet'], errors='coerce')
df0['win'] = pd.to_numeric(df0['win'], errors='coerce')
df0['time'] = pd.to_numeric(df0['time'], errors='coerce')

# Ensure user_id is string for join
df0['user_id'] = df0['user_id'].astype(str)
df1['user_id'] = df1['user_id'].astype(str)

# Merge on user_id (inner join to keep only matching users)
merged = pd.merge(df0, df1, on='user_id', how='inner')

# Extract numeric part of user_id for grouping and convert to Int64
merged['user_id'] = pd.to_numeric(merged['user_id'].str.extract('(\d+)')[0], errors='coerce').astype('Int64')

# Convert geo to string
merged['geo'] = merged['geo'].astype(str)

# Convert email to numeric by extracting digits, then to Int64
merged['email'] = pd.to_numeric(merged['email'].str.extract('(\d+)')[0], errors='coerce').astype('Int64')

# Fill NaN in numeric columns with 0 before aggregation
merged['time'] = merged['time'].fillna(0).astype('Int64')
merged['bet'] = merged['bet'].fillna(0).astype('Int64')
merged['win'] = merged['win'].fillna(0).astype('Int64')
merged['email'] = merged['email'].fillna(0).astype('Int64')

# Group by geo and user_id, aggregate sums of time, bet, win, email
grouped = merged.groupby(['geo', 'user_id'], as_index=False).agg({
    'time': 'sum',
    'bet': 'sum',
    'win': 'sum',
    'email': 'sum'
})

# Write output with exact target schema column order
grouped = grouped[['geo', 'user_id', 'time', 'bet', 'win', 'email']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_33/target_multisource_mcts.csv", index=False)