import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length2_33/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length2_33/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_33/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

df0['user_id'] = df0['user_id'].str.replace('user_', '', regex=False)
df0['user_id'] = pd.to_numeric(df0['user_id'], errors='coerce')

df0['time'] = pd.to_numeric(df0['time'], errors='coerce')
df0['bet'] = pd.to_numeric(df0['bet'], errors='coerce')
df0['win'] = pd.to_numeric(df0['win'], errors='coerce')

grouped = df0.groupby(['user_id']).agg({'time':'min', 'bet':'min', 'win':'min'}).reset_index()

df1['user_id'] = df1['user_id'].str.replace('user_', '', regex=False)
df1['user_id'] = pd.to_numeric(df1['user_id'], errors='coerce')

merged = pd.merge(grouped, df1, on='user_id', how='inner')

merged = merged.rename(columns={'geo':'geo', 'user_id':'user_id', 'time':'time', 'bet':'bet', 'win':'win', 'email':'email'})

merged = merged[['geo', 'user_id', 'time', 'bet', 'win', 'email']]

merged['user_id'] = merged['user_id'].astype('Int64')
merged['time'] = merged['time'].astype('Int64')
merged['bet'] = merged['bet'].astype('Int64')
merged['win'] = merged['win'].astype('Int64')
merged['email'] = pd.to_numeric(merged['email'], errors='coerce').astype('Int64')

merged.to_csv(target_path, index=False)