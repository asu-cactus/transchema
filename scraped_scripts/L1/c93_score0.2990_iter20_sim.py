import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on=["user_id", "time"], how="inner", suffixes=('', '_dup'))

grouped = df_joined.groupby('user_id', as_index=False).agg({
    'time': 'first',
    'bet': 'sum',
    'win': 'sum'
})

grouped['user_id'] = grouped['user_id'].astype(str)
grouped['time'] = grouped['time'].astype(str)
grouped['bet'] = grouped['bet'].astype(float)
grouped['win'] = grouped['win'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)