import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_3.csv", index_col=0)

df12 = pd.merge(df1, df2, on="County", how="inner")
df012 = pd.merge(df12, df0, on="County", how="inner")
df_all = pd.merge(df012, df3, on="County", how="inner")

df_all = df_all[['County', 'm1401', 'm1403']]

df_grouped = df_all.groupby(['County', 'm1401'], dropna=False, as_index=False).agg({'m1403': 'first'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_36/target_multisource_mcts.csv", index=False)