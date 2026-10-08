import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_33/training_1.csv", index_col=0)

# Process df0
df0['user_id'] = df0['user_id'].str.replace('user_', '', regex=False)
df0['user_id'] = pd.to_numeric(df0['user_id'], errors='coerce')

# Convert 'time' to datetime, then to integer timestamp (e.g., Unix timestamp)
df0['time'] = pd.to_datetime(df0['time'], errors='coerce')
df0['time'] = df0['time'].astype('int64') // 10**9  # convert to seconds since epoch

df0['bet'] = pd.to_numeric(df0['bet'], errors='coerce').fillna(0).astype(int)
df0['win'] = pd.to_numeric(df0['win'], errors='coerce').fillna(0).astype(int)

# Process df1
df1['user_id'] = df1['user_id'].str.replace('user_', '', regex=False)
df1['user_id'] = pd.to_numeric(df1['user_id'], errors='coerce')
df1['geo'] = df1['geo'].astype(str)
df1['email'] = df1['email'].astype(str)  # keep as string for now

# Join on user_id
merged = pd.merge(df0, df1, on='user_id', how='inner')

# Convert email to categorical codes (integer)
merged['email'] = merged['email'].astype('category').cat.codes

# Group by geo and user_id
grouped = merged.groupby(['geo', 'user_id'], as_index=False).agg({
    'time': 'max',
    'bet': 'sum',
    'win': 'sum',
    'email': 'max'
})

# Reorder columns to match target schema
grouped = grouped[['geo', 'user_id', 'time', 'bet', 'win', 'email']]

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_33/target_multisource_mcts.csv", index=False)