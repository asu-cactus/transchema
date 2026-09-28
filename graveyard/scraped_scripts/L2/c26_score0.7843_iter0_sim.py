import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

df1['time'] = pd.to_datetime(df1['time'], errors='coerce')
df1['time'] = df1['time'].dt.day.fillna(0).astype(int)
df1['bet'] = pd.to_numeric(df1['bet'], errors='coerce').fillna(0).astype(int)
df1['win'] = pd.to_numeric(df1['win'], errors='coerce').fillna(0).astype(int)

grouped_source1 = df1.groupby('user_id', as_index=False).agg({
    'time': 'sum',
    'bet': 'sum',
    'win': 'sum'
})

df0['email'] = df0['email'].str.len()
df0['geo'] = df0['geo'].str.len()

grouped_source0 = df0.groupby('user_id', as_index=False).agg({
    'email': 'sum',
    'geo': 'sum'
})

result = pd.merge(grouped_source1, grouped_source0, on='user_id', how='inner')

result = result[['user_id', 'time', 'bet', 'win', 'email', 'geo']]

result.to_csv(target_path, index=False)