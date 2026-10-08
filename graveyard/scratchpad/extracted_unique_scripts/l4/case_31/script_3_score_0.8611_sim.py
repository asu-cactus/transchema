import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

df_23 = pd.merge(df2, df3, on="County", how="outer")
df_230 = pd.merge(df_23, df0, on="County", how="outer")
df_final = pd.merge(df_230, df4, on="County", how="outer")

df_final = df_final[['County', 'm1401', 'm1402', 'm1403', 'm1404']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv", index=False)