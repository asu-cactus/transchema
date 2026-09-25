import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_0.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_2.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_1.csv", index_col=0)

df_union = pd.concat([s0, s2], ignore_index=True)

df_union['year'] = pd.to_datetime(df_union['date'], errors='coerce').dt.year
df_union = df_union.drop(columns=['date'])

df_joined = pd.merge(df_union, s1, on=['state', 'year'], how='inner')

df_joined['draw_sales'] = pd.to_numeric(df_joined['draw_sales'], errors='coerce').fillna(0).astype(int)
df_joined['full_state'] = pd.to_numeric(df_joined['full_state'], errors='coerce').fillna(0).astype(int)
df_joined['pop'] = pd.to_numeric(df_joined['pop'], errors='coerce').fillna(0).astype(int)
df_joined['year'] = df_joined['year'].astype(int)
df_joined['state'] = df_joined['state'].astype(str)

result = df_joined[['state', 'year', 'draw_sales', 'full_state', 'pop']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_6/target_multisource_mcts.csv", index=False)