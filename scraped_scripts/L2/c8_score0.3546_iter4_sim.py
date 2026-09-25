import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_1.csv", index_col=0)

df_merged = pd.merge(df0, df1, on="Mouse ID")

df_grouped = df_merged.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).agg({
    "Timepoint": "mean"
})

df_grouped["Timepoint"] = df_grouped["Timepoint"].round().astype(int)
df_grouped["Mouse ID"] = df_grouped["Mouse ID"].astype(str)

df_result = df_grouped[["Drug", "Timepoint", "Mouse ID"]]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length2_8/target_multisource_mcts.csv", index=False)