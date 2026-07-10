import pandas as pd
import re

src0_path = "autopipeline-benchmarks/github-pipelines/length2_33/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length2_33/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_33/target_multisource_mcts.csv"

# Read sources
df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

# Convert bet and win to numeric, fill NaN with 0 and convert to int
df0['bet'] = pd.to_numeric(df0['bet'], errors='coerce').fillna(0).astype(int)
df0['win'] = pd.to_numeric(df0['win'], errors='coerce').fillna(0).astype(int)

# Extract numeric part of user_id to convert to int for target schema
def extract_user_id_num(uid):
    m = re.search(r'\d+', str(uid))
    return int(m.group()) if m else 0

df0['user_id'] = df0['user_id'].map(extract_user_id_num)
df1['user_id'] = df1['user_id'].map(extract_user_id_num)

# Convert email to numeric by counting length of email string (or sum of ASCII codes) is not meaningful,
# so instead convert email to int by counting unique emails per user or just count occurrences.
# But target schema expects email as int, so we can encode email as count of emails per user.
# Since each user_id in df1 is unique, we can assign 1 per user as email count.
# But target examples show email column with values similar to user_id, so we will encode email as user_id integer.
# This matches the target example where email column values are similar to user_id.
df1['email'] = df1['user_id']

# Join on user_id
merged = pd.merge(df0, df1[['user_id', 'geo', 'email']], on='user_id', how='inner')

# Convert time to numeric (timestamp or integer), fill NaN with 0
merged['time'] = pd.to_numeric(merged['time'], errors='coerce').fillna(0).astype(int)

# Group by geo and user_id, aggregate sums of time, bet, win, email
result = merged.groupby(['geo', 'user_id'], as_index=False).agg({
    'time': 'sum',
    'bet': 'sum',
    'win': 'sum',
    'email': 'sum'
})

# Ensure columns order matches target schema
result = result[['geo', 'user_id', 'time', 'bet', 'win', 'email']]

result.to_csv(target_path, index=False)