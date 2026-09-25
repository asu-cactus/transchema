import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_grouped = df.groupby('TransTo', dropna=True)['WarNum'].nunique().reset_index()
df_grouped.columns = ['TransTo', 'WarNum']
df_grouped['TransTo'] = df_grouped['TransTo'].astype('Int64')
df_grouped['WarNum'] = df_grouped['WarNum'].astype('Int64')

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_57/target_multisource_mcts.csv", index=False)