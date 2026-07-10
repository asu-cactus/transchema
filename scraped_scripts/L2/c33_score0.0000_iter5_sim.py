import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_33/training_1.csv", index_col=0)

df0['bet'] = pd.to_numeric(df0['bet'], errors='coerce')
df0['win'] = pd.to_numeric(df0['win'], errors='coerce')

df0['user_id'] = df0['user_id'].astype(str)
df1['user_id'] = df1['user_id'].astype(str)

pivot = df0.groupby(['user_id', 'time'], as_index=False).agg({'bet':'sum', 'win':'sum'})

merged = pd.merge(pivot, df1, on='user_id', how='inner')

merged['time'] = pd.to_numeric(merged['time'], errors='coerce')
merged['email'] = merged['email'].astype(str)
merged['geo'] = merged['geo'].astype(str)

grouped = merged.groupby(['geo', 'user_id', 'time', 'email'], as_index=False).agg({'bet':'sum', 'win':'sum'})

grouped['user_id'] = pd.to_numeric(grouped['user_id'].str.extract('(\d+)')[0], errors='coerce').astype('Int64')
grouped['email'] = pd.to_numeric(grouped['email'].str.extract('(\d+)')[0], errors='coerce').astype('Int64')
grouped['time'] = grouped['time'].astype('Int64')
grouped['bet'] = grouped['bet'].fillna(0).astype('Int64')
grouped['win'] = grouped['win'].fillna(0).astype('Int64')

grouped = grouped.rename(columns={'geo':'geo', 'user_id':'user_id', 'time':'time', 'bet':'bet', 'win':'win', 'email':'email'})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_33/target_multisource_mcts.csv", index=False)