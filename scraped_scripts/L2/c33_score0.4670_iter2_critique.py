import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length2_33/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length2_33/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_33/target_multisource_mcts.csv"

# Read source tables
df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

# Clean and convert user_id to integer in both tables
df0['user_id'] = df0['user_id'].str.replace('user_', '', regex=False)
df0['user_id'] = pd.to_numeric(df0['user_id'], errors='coerce')

df1['user_id'] = df1['user_id'].str.replace('user_', '', regex=False)
df1['user_id'] = pd.to_numeric(df1['user_id'], errors='coerce')

# Join on user_id
merged = pd.merge(df0, df1, on='user_id', how='inner')

# Group by geo and user_id
# Aggregations:
# - time: count of non-null time values
# - bet: sum
# - win: sum
# - email: count distinct emails (since email is string, target expects int)
agg = merged.groupby(['geo', 'user_id']).agg(
    time=('time', 'count'),
    bet=('bet', 'sum'),
    win=('win', 'sum'),
    email=('email', pd.Series.nunique)
).reset_index()

# Convert columns to appropriate types
agg['user_id'] = agg['user_id'].astype('Int64')
agg['time'] = agg['time'].fillna(0).astype('Int64')
agg['bet'] = agg['bet'].fillna(0).astype('Int64')
agg['win'] = agg['win'].fillna(0).astype('Int64')
agg['email'] = agg['email'].fillna(0).astype('Int64')

# Reorder columns to match target schema
result = agg[['geo', 'user_id', 'time', 'bet', 'win', 'email']]

# Write to target path
result.to_csv(target_path, index=False)