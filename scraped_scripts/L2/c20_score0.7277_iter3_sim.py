import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_20/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_20/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID")

grouped = merged.groupby(["Drug", "Timepoint"]).agg({"Mouse ID": "count"}).reset_index()

grouped = grouped.rename(columns={"Drug": "Drug", "Timepoint": "Timepoint", "Mouse ID": "Mouse ID"})

grouped["Mouse ID"] = grouped["Mouse ID"].astype(int)
grouped["Timepoint"] = grouped["Timepoint"].astype(int)
grouped["Drug"] = grouped["Drug"].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_20/target_multisource_mcts.csv", index=False)