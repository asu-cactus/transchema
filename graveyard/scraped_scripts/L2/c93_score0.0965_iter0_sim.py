import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_93/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_93/training_1.csv", index_col=0)

df_join = pd.merge(df0, df1, on="Mouse ID", how="inner")

df_join["Mouse ID"] = pd.to_numeric(df_join["Mouse ID"], errors='coerce').astype('Int64')
df_join["Timepoint"] = pd.to_numeric(df_join["Timepoint"], errors='coerce').astype('Int64')
df_join["Drug"] = df_join["Drug"].astype(str)

df_target = df_join[["Drug", "Timepoint", "Mouse ID"]]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length2_93/target_multisource_mcts.csv", index=False)