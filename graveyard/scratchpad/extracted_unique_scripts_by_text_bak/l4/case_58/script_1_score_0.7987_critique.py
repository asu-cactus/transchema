import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_58/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df["TransTo"] = df["TransTo"].fillna(0)

df_grouped = df.groupby("WarNum", as_index=False).agg({"TransTo": "min"})

df_grouped["WarNum"] = df_grouped["WarNum"].astype(int)
df_grouped["TransTo"] = df_grouped["TransTo"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_58/target_multisource_mcts.csv", index=False)