import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_4.csv", index_col=0)

join_cols = ['Year', 'Category', 'Nominee', 'Movie', 'Winner']
df0_1_joined = pd.merge(df0, df1, on=join_cols, how='inner', suffixes=('_0', '_1'))

df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

df_all = df_all.astype(str)

df_all = df_all[join_cols]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_65/target_multisource_mcts.csv", index=False)