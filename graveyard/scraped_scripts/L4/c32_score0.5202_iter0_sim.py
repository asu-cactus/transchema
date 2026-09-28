import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_0.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_4.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_32/training_3.csv", index_col=0)

df_r1403 = pd.concat([df0, df4], ignore_index=True)
df_r1403 = df_r1403.rename(columns={"r1403": "r1403_x"})
df_r1403["r1403_y"] = df_r1403["r1403_x"]

df = df_r1403.merge(df3, on="County", how="outer")
df = df.rename(columns={"r1401": "r1401"})

df = df.merge(df2, on="County", how="outer")
df = df.rename(columns={"r1402": "r1402"})

df = df.merge(df1, on="County", how="outer")

df = df[["County", "r1401", "r1402", "r1403_x", "r1403_y"]]

df = df.groupby(["County", "r1401", "r1402", "r1403_x", "r1403_y"], dropna=False).size().reset_index().drop(columns=0)

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_32/target_multisource_mcts.csv", index=False)