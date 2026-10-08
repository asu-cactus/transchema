import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_33/training_1.csv", index_col=0)

df0['user_id'] = df0['user_id'].str.replace('user_', '', regex=False)
df0['user_id'] = pd.to_numeric(df0['user_id'], errors='coerce')
df0['time'] = pd.to_numeric(df0['time'], errors='coerce')
df0['bet'] = pd.to_numeric(df0['bet'], errors='coerce').fillna(0).astype(int)
df0['win'] = pd.to_numeric(df0['win'], errors='coerce').fillna(0).astype(int)

df1['user_id'] = df1['user_id'].str.replace('user_', '', regex=False)
df1['user_id'] = pd.to_numeric(df1['user_id'], errors='coerce')
df1['email'] = df1['email'].str.extract(r'(\d+)').fillna(0).astype(int)
df1['geo'] = df1['geo'].astype(str)

merged = pd.merge(df0, df1, on='user_id', how='inner')

grouped = merged.groupby('geo').agg({
    'user_id': 'max',
    'time': 'max',
    'bet': 'sum',
    'win': 'sum',
    'email': 'max'
}).reset_index()

grouped = grouped[['geo', 'user_id', 'time', 'bet', 'win', 'email']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_33/target_multisource_mcts.csv", index=False)