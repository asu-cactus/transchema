import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

df_23 = pd.merge(df2, df3, on="County", how="outer")
df_230 = pd.merge(df_23, df0, on="County", how="outer")
df_2304 = pd.merge(df_230, df4, on="County", how="outer")
df_all = pd.merge(df_2304, df1, on="County", how="outer")

result = df_all.groupby(['County', 'm1401', 'm1402', 'm1403', 'm1404'], dropna=False, as_index=False).size()

result = result.drop(columns='size')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv", index=False)