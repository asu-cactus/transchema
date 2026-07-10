import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)
df0['user_id'] = df0['user_id'].str.replace(r'^Запись пользователя № - ', '', regex=True)
df0['bet'] = pd.to_numeric(df0['bet'], errors='coerce')
df0['win'] = pd.to_numeric(df0['win'], errors='coerce')
df0 = df0[['user_id', 'time', 'bet', 'win']]
df0 = df0.groupby('user_id', as_index=False).first()
df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)