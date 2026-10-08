import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

# Start join from Source1 (df1) which has only 'County' column
df_12 = pd.merge(df1, df2, on="County", how="inner")
df_123 = pd.merge(df_12, df3, on="County", how="inner")
df_1230 = pd.merge(df_123, df0, on="County", how="inner")
df_final = pd.merge(df_1230, df4, on="County", how="inner")

df_final = df_final[['County', 'm1401', 'm1402', 'm1403', 'm1404']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv", index=False)