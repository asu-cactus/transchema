import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)

df = df0.copy()

# Ensure correct dtypes
df['user_id'] = df['user_id'].astype(str)
df['time'] = df['time'].astype(str)
df['bet'] = pd.to_numeric(df['bet'], errors='coerce')
df['win'] = pd.to_numeric(df['win'], errors='coerce')

# Group by user_id and time, aggregate bet and win by mean
df_grouped = df.groupby(['user_id', 'time'], as_index=False).agg({'bet': 'mean', 'win': 'mean'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)