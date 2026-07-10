import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv", index_col=0)

# Convert email and geo to their string lengths
df0['email'] = df0['email'].str.len()
df0['geo'] = df0['geo'].str.len()

# Convert bet and win to numeric, fill NaN with 0, and convert to int
df1['bet'] = pd.to_numeric(df1['bet'], errors='coerce').fillna(0).astype(int)
df1['win'] = pd.to_numeric(df1['win'], errors='coerce').fillna(0).astype(int)

# Join on user_id
merged = pd.merge(df1, df0, on='user_id', how='inner')

# Aggregate:
# time: count of rows per user (number of bets)
# bet: sum per user
# win: sum per user
# email, geo: take first (unique per user)
agg = merged.groupby('user_id').agg({
    'time': 'count',
    'bet': 'sum',
    'win': 'sum',
    'email': 'first',
    'geo': 'first'
}).reset_index()

# Ensure columns are in target order
agg = agg[['user_id', 'time', 'bet', 'win', 'email', 'geo']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv", index=False)