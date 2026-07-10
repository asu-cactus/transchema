import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Convert time to datetime to handle missing or invalid times
df1['time'] = pd.to_datetime(df1['time'], errors='coerce')

# Aggregate Source1 by user_id
agg = df1.groupby('user_id').agg(
    time=('time', 'count'),  # count of non-null time entries per user
    bet=('bet', 'sum'),
    win=('win', 'sum')
).reset_index()

# Merge Source0 and aggregated Source1 on user_id with outer join to keep all users
merged = pd.merge(df0, agg, on='user_id', how='left')

# Replace NaN in numeric columns with 0 (for users with no bets/wins/time)
merged['time'] = merged['time'].fillna(0).astype(int)
merged['bet'] = merged['bet'].fillna(0).astype(int)
merged['win'] = merged['win'].fillna(0).astype(int)

# Convert email and geo strings to their lengths as integers
merged['email'] = merged['email'].str.len()
merged['geo'] = merged['geo'].str.len()

# Select columns in target schema order
result = merged[['user_id', 'time', 'bet', 'win', 'email', 'geo']]

result.to_csv(target_path, index=False)