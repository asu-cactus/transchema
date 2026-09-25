import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv", index_col=0)

df1['time'] = pd.to_datetime(df1['time'], errors='coerce')
df1['time_int'] = df1['time'].dt.day.fillna(0).astype(int)

agg = df1.groupby(['user_id']).agg(
    time=('time_int', 'nunique'),
    bet=('bet', 'sum'),
    win=('win', 'sum')
).reset_index()

df = pd.merge(df0, agg, on='user_id', how='inner')

df['email'] = df['email'].str.len()
df['geo'] = df['geo'].str.len()

df = df.rename(columns={'user_id': 'user_id', 'time': 'time', 'bet': 'bet', 'win': 'win', 'email': 'email', 'geo': 'geo'})

df = df[['user_id', 'time', 'bet', 'win', 'email', 'geo']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv", index=False)