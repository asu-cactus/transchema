import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv", index_col=0)

df1['time'] = pd.to_datetime(df1['time'], errors='coerce').dt.hour
df1['bet'] = pd.to_numeric(df1['bet'], errors='coerce').fillna(0).astype(int)
df1['win'] = pd.to_numeric(df1['win'], errors='coerce').fillna(0).astype(int)

agg = df1.groupby('user_id').agg({'time':'max', 'bet':'max', 'win':'max'}).reset_index()

df0['email'] = df0['email'].str.len()
df0['geo'] = df0['geo'].str.len()

result = pd.merge(agg, df0, on='user_id', how='inner')

result = result[['user_id', 'time', 'bet', 'win', 'email', 'geo']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv", index=False)