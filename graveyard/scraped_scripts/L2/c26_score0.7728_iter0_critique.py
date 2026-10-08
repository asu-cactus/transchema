import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

# Convert time to day of month as integer
df1['time'] = pd.to_datetime(df1['time'], errors='coerce').dt.day.fillna(0).astype(int)
df1['bet'] = pd.to_numeric(df1['bet'], errors='coerce').fillna(0).astype(int)
df1['win'] = pd.to_numeric(df1['win'], errors='coerce').fillna(0).astype(int)

# Convert email and geo to their string lengths (no aggregation needed if user_id unique)
df0['email'] = df0['email'].str.len()
df0['geo'] = df0['geo'].str.len()

# Join on user_id
merged = pd.merge(df1, df0[['user_id', 'email', 'geo']], on='user_id', how='inner')

# Group by user_id and aggregate time, bet, win by sum
result = merged.groupby('user_id', as_index=False).agg({
    'time': 'sum',
    'bet': 'sum',
    'win': 'sum',
    'email': 'first',  # email and geo are unique per user_id, so take first
    'geo': 'first'
})

result = result[['user_id', 'time', 'bet', 'win', 'email', 'geo']]

result.to_csv(target_path, index=False)