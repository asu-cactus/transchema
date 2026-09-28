import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_filtered = df_all[df_all["TransTo"].notna()]

df_filtered["TransTo"] = df_filtered["TransTo"].astype("Int64")
df_filtered["WarNum"] = df_filtered["WarNum"].astype("Int64")

df_unique = df_filtered.drop_duplicates(subset=["TransTo", "WarNum"])

df_unique.to_csv("autopipeline-benchmarks/github-pipelines/length4_57/target_multisource_mcts.csv", index=False)