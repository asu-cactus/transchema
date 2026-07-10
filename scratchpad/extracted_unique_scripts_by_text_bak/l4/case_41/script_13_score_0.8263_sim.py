import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

agg_0 = df0.groupby(['x', 'label'], as_index=False)['y'].mean()
agg_1 = df1.groupby(['x', 'label'], as_index=False)['y'].mean()
agg_2 = df2.groupby(['x', 'label'], as_index=False)['y'].mean()
agg_3 = df3.groupby(['x', 'label'], as_index=False)['y'].mean()

df_all = pd.concat([agg_0, agg_1, agg_2, agg_3], ignore_index=True)

df_all['label'], _ = pd.factorize(df_all['label'])
df_all['x'] = df_all['x'].round().astype(int)
df_all = df_all.rename(columns={'y': 'y', 'x': 'x', 'label': 'label'})

df_all = df_all[['y', 'x', 'label']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)