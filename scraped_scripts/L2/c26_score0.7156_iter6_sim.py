import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

df1['time'] = pd.to_datetime(df1['time'], errors='coerce').dt.hour.fillna(0).astype(int)
df1['bet'] = pd.to_numeric(df1['bet'], errors='coerce').fillna(0).astype(int)
df1['win'] = pd.to_numeric(df1['win'], errors='coerce').fillna(0).astype(int)

grouped = df1.groupby(['user_id', 'time'], as_index=False).agg({'bet':'sum', 'win':'sum'})

merged = pd.merge(grouped, df0, on='user_id', how='left')

merged['email'] = pd.to_numeric(merged['email'], errors='coerce').fillna(0).astype(int)
merged['geo'] = pd.to_numeric(merged['geo'], errors='coerce').fillna(0).astype(int)

merged = merged[['user_id', 'time', 'bet', 'win', 'email', 'geo']]

merged.to_csv(target_path, index=False)