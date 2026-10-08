import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length2_33/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length2_33/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_33/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

df0['bet'] = pd.to_numeric(df0['bet'], errors='coerce').fillna(0).astype(int)
df0['win'] = pd.to_numeric(df0['win'], errors='coerce').fillna(0).astype(int)

grouped = df0.groupby(['user_id', 'time'], as_index=False).agg({'bet':'sum', 'win':'sum'})

df1['email'] = pd.to_numeric(df1['email'], errors='coerce')
df1['email'] = df1['email'].fillna(0).astype(int)

merged = pd.merge(grouped, df1, on='user_id', how='inner')

merged['time'] = pd.to_numeric(merged['time'], errors='coerce').fillna(0).astype(int)

result = merged[['geo', 'user_id', 'time', 'bet', 'win', 'email']]

result.to_csv(target_path, index=False)