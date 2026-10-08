import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length2_33/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length2_33/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_33/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

df0['user_id'] = df0['user_id'].str.replace('user_', '', regex=False)
df0['user_id'] = pd.to_numeric(df0['user_id'], errors='coerce')

agg = df0.groupby(['user_id']).agg(
    time=('time', 'count'),
    bet=('bet', 'sum'),
    win=('win', 'sum')
).reset_index()

df1['user_id'] = df1['user_id'].str.replace('user_', '', regex=False)
df1['user_id'] = pd.to_numeric(df1['user_id'], errors='coerce')

merged = pd.merge(agg, df1, on='user_id', how='inner')

result = merged.rename(columns={
    'time': 'time',
    'bet': 'bet',
    'win': 'win',
    'geo': 'geo',
    'email': 'email',
    'user_id': 'user_id'
})[['geo', 'user_id', 'time', 'bet', 'win', 'email']]

result['user_id'] = result['user_id'].astype('Int64')
result['time'] = result['time'].fillna(0).astype('Int64')
result['bet'] = result['bet'].fillna(0).astype('Int64')
result['win'] = result['win'].fillna(0).astype('Int64')
result['email'] = pd.to_numeric(result['email'], errors='coerce').astype('Int64')

result.to_csv(target_path, index=False)