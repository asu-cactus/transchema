import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_39/training_1.csv", index_col=0)

df_merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

df_result = df_merged[["Drug", "Timepoint", "Mouse ID"]].copy()

df_result["Drug"] = df_result["Drug"].astype(str)
df_result["Timepoint"] = pd.to_numeric(df_result["Timepoint"], errors='coerce').astype("Int64")
df_result["Mouse ID"] = pd.to_numeric(df_result["Mouse ID"], errors='coerce').astype("Int64")

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length2_39/target_multisource_mcts.csv", index=False)