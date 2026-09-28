import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)

df_grouped = df0.groupby('time', as_index=False).agg({'user_id': 'first', 'bet': 'sum', 'win': 'sum'})

df_grouped['user_id'] = df_grouped['user_id'].astype(str)
df_grouped['time'] = df_grouped['time'].astype(str)
df_grouped['bet'] = df_grouped['bet'].astype(float)
df_grouped['win'] = df_grouped['win'].astype(float)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)