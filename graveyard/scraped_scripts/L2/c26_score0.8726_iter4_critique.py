import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

# Convert bet and win to int, fill NaN with 0
df1['bet'] = pd.to_numeric(df1['bet'], errors='coerce').fillna(0).astype(int)
df1['win'] = pd.to_numeric(df1['win'], errors='coerce').fillna(0).astype(int)

# Convert time to indicator (1 if not null, else 0)
df1['time'] = df1['time'].notna().astype(int)

# Join on user_id only
df_merged = pd.merge(df1, df0[['user_id', 'email', 'geo']], on='user_id', how='inner')

# Group by user_id only, aggregate bet and win by sum, time by sum (count of non-null),
# email and geo by first (since they are unique per user_id)
grouped = df_merged.groupby('user_id', as_index=False).agg({
    'bet': 'sum',
    'win': 'sum',
    'time': 'sum',
    'email': 'first',
    'geo': 'first'
})

# Convert email string to length of string (integer)
grouped['email'] = grouped['email'].astype(str).apply(len).astype(int)

# Convert geo string to categorical codes (integer)
grouped['geo'] = grouped['geo'].astype('category').cat.codes.astype(int)

# Ensure types and order columns as per target schema
grouped = grouped.astype({
    'user_id': str,
    'time': int,
    'bet': int,
    'win': int,
    'email': int,
    'geo': int
})

grouped = grouped[['user_id', 'time', 'bet', 'win', 'email', 'geo']]

grouped.to_csv(target_path, index=False)