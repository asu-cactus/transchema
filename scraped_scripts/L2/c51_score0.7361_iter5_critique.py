import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Group by Drug and Timepoint, count distinct Mouse ID
result = merged.groupby(["Drug", "Timepoint"], as_index=False).agg({"Mouse ID": pd.Series.nunique})

# Ensure types match target schema
result["Drug"] = result["Drug"].astype(str)
result["Timepoint"] = result["Timepoint"].astype(int)
result["Mouse ID"] = result["Mouse ID"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_51/target_multisource_mcts.csv", index=False)