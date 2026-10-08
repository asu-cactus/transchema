import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_48/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_48/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Group by Drug and Timepoint, aggregate Mouse ID by count distinct
result = merged.groupby(["Drug", "Timepoint"], as_index=False).agg({"Mouse ID": pd.Series.nunique})

# Rename columns to match target schema exactly
# "Mouse ID" is count of unique mice, so integer type
result["Timepoint"] = result["Timepoint"].astype(int)
result["Mouse ID"] = result["Mouse ID"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_48/target_multisource_mcts.csv", index=False)