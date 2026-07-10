import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length2_33/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length2_33/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_33/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

df0['user_id'] = df0['user_id'].astype(str)
df1['user_id'] = df1['user_id'].astype(str)

agg = df0.groupby(['user_id', 'time'], dropna=False).agg(
    bet_min=pd.NamedAgg(column='bet', aggfunc='min'),
    bet_max=pd.NamedAgg(column='bet', aggfunc='max'),
    win_min=pd.NamedAgg(column='win', aggfunc='min'),
    win_max=pd.NamedAgg(column='win', aggfunc='max')
).reset_index()

agg['bet'] = agg[['bet_min', 'bet_max']].min(axis=1).fillna(0).astype(int)
agg['win'] = agg[['win_min', 'win_max']].min(axis=1).fillna(0).astype(int)

agg = agg.drop(columns=['bet_min', 'bet_max', 'win_min', 'win_max'])

merged = pd.merge(agg, df1, on='user_id', how='inner')

merged['geo'] = merged['geo'].astype(str)
merged['email'] = pd.to_numeric(merged['email'], errors='coerce').fillna(0).astype(int)
merged['user_id'] = merged['user_id'].str.extract('(\d+)').astype(int)
merged['time'] = pd.to_numeric(merged['time'], errors='coerce').fillna(0).astype(int)
merged['bet'] = merged['bet'].fillna(0).astype(int)
merged['win'] = merged['win'].fillna(0).astype(int)

result = merged[['geo', 'user_id', 'time', 'bet', 'win', 'email']]

result.to_csv(target_path, index=False)