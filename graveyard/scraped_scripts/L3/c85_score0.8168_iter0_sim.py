import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_3.csv", index_col=0)

df_2_0 = pd.merge(df2, df0, on="County", how="inner")
df_2_0_1 = pd.merge(df_2_0, df1, on="County", how="inner")

df_2_0_1 = df_2_0_1.rename(columns={"m1402": "m1403"})

df_2_0_1 = df_2_0_1[["County", "m1401", "m1403"]]

df_2_0_1.to_csv("autopipeline-benchmarks/github-pipelines/length3_85/target_multisource_mcts.csv", index=False)